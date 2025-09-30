import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import * as Y from 'yjs';
import * as awarenessProtocol from 'y-protocols/awareness';
import * as syncProtocol from 'y-protocols/sync';
import * as encoding from 'lib0/encoding';
import * as decoding from 'lib0/decoding';
import * as mutex from 'lib0/mutex';
import { createClient } from 'redis';
import pino from 'pino';
import { v4 as uuidv4 } from 'uuid';
import { config } from './config.js';
import { EventStoreClient } from './event-store-client.js';
import { initTelemetry } from './telemetry.js';
import { metrics } from './metrics.js';

const logger = pino({
  level: 'info',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'SYS:standard'
    }
  }
});

// Message types for WebSocket communication
const messageSync = 0;
const messageAwareness = 1;
const messageAuth = 2;
const messagePresence = 3;

interface ConnectedClient {
  id: string;
  ws: any;
  doc: Y.Doc;
  awareness: awarenessProtocol.Awareness;
  rooms: Set<string>;
  userId?: string;
}

interface Room {
  name: string;
  doc: Y.Doc;
  awareness: awarenessProtocol.Awareness;
  clients: Set<ConnectedClient>;
  lastActivity: number;
  persistenceKey: string;
}

class CollaborationServer {
  private app: express.Application;
  private server: any;
  private wss: WebSocketServer;
  private redis: any;
  private eventStore: EventStoreClient;
  private rooms = new Map<string, Room>();
  private clients = new Map<string, ConnectedClient>();
  private mutexes = new Map<string, mutex.mutex>();
  
  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server });
    this.eventStore = new EventStoreClient(config.eventStoreUrl);
    
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
  }

  private setupMiddleware(): void {
    this.app.use(express.json());
    this.app.use((req, res, next) => {
      logger.info({ method: req.method, url: req.url }, 'HTTP request');
      next();
    });
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'collab-engine',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        rooms: this.rooms.size,
        clients: this.clients.size
      });
    });

    // Metrics endpoint
    this.app.get('/metrics', async (req, res) => {
      try {
        const metricsText = await metrics.getMetrics();
        res.set('Content-Type', 'text/plain');
        res.send(metricsText);
      } catch (error) {
        logger.error({ error }, 'Failed to get metrics');
        res.status(500).json({ error: 'Failed to get metrics' });
      }
    });

    // Room information
    this.app.get('/rooms/:roomName', (req, res) => {
      const room = this.rooms.get(req.params.roomName);
      if (!room) {
        return res.status(404).json({ error: 'Room not found' });
      }

      res.json({
        name: room.name,
        clients: room.clients.size,
        lastActivity: room.lastActivity,
        docSize: Y.encodeStateAsUpdate(room.doc).length
      });
    });

    // List all rooms
    this.app.get('/rooms', (req, res) => {
      const roomList = Array.from(this.rooms.values()).map(room => ({
        name: room.name,
        clients: room.clients.size,
        lastActivity: room.lastActivity,
        docSize: Y.encodeStateAsUpdate(room.doc).length
      }));

      res.json({ rooms: roomList });
    });

    // Presence information
    this.app.get('/rooms/:roomName/presence', (req, res) => {
      const room = this.rooms.get(req.params.roomName);
      if (!room) {
        return res.status(404).json({ error: 'Room not found' });
      }

      const presence = Array.from(room.clients).map(client => ({
        id: client.id,
        userId: client.userId,
        awareness: room.awareness.getStates().get(parseInt(client.id)) || {}
      }));

      res.json({ presence });
    });
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws, req) => {
      const clientId = uuidv4();
      const client: ConnectedClient = {
        id: clientId,
        ws,
        doc: new Y.Doc(),
        awareness: new awarenessProtocol.Awareness(new Y.Doc()),
        rooms: new Set()
      };

      this.clients.set(clientId, client);
      metrics.incrementActiveConnections();

      logger.info({ clientId }, 'Client connected');

      ws.on('message', async (message: Buffer) => {
        try {
          await this.handleMessage(client, message);
        } catch (error) {
          logger.error({ error, clientId }, 'Error handling message');
          metrics.incrementErrorCount();
        }
      });

      ws.on('close', () => {
        this.handleDisconnect(client);
      });

      ws.on('error', (error) => {
        logger.error({ error, clientId }, 'WebSocket error');
        metrics.incrementErrorCount();
      });

      // Send initial sync
      this.sendSync(client, encoding.createEncoder());
    });
  }

  private async handleMessage(client: ConnectedClient, message: Buffer): Promise<void> {
    const decoder = decoding.createDecoder(message);
    const messageType = decoding.readVarUint(decoder);

    switch (messageType) {
      case messageSync:
        await this.handleSyncMessage(client, decoder);
        break;
      case messageAwareness:
        await this.handleAwarenessMessage(client, decoder);
        break;
      case messageAuth:
        await this.handleAuthMessage(client, decoder);
        break;
      case messagePresence:
        await this.handlePresenceMessage(client, decoder);
        break;
      default:
        logger.warn({ messageType }, 'Unknown message type');
    }
  }

  private async handleSyncMessage(client: ConnectedClient, decoder: any): Promise<void> {
    const roomName = decoding.readVarString(decoder);
    const room = await this.getOrCreateRoom(roomName);
    
    if (!client.rooms.has(roomName)) {
      client.rooms.add(roomName);
      room.clients.add(client);
      
      // Set up awareness for this room
      client.awareness = room.awareness;
      metrics.incrementRoomJoins();
    }

    const encoder = encoding.createEncoder();
    encoding.writeVarUint(encoder, messageSync);
    encoding.writeVarString(encoder, roomName);
    
    syncProtocol.readSyncMessage(decoder, encoder, room.doc, null);
    
    if (encoding.length(encoder) > 1) {
      client.ws.send(encoding.toUint8Array(encoder));
    }

    room.lastActivity = Date.now();
  }

  private async handleAwarenessMessage(client: ConnectedClient, decoder: any): Promise<void> {
    const roomName = decoding.readVarString(decoder);
    const room = this.rooms.get(roomName);
    
    if (!room || !client.rooms.has(roomName)) {
      logger.warn({ roomName }, 'Client not in room for awareness message');
      return;
    }

    awarenessProtocol.applyAwarenessUpdate(room.awareness, decoding.readVarUint8Array(decoder), client);
    
    // Broadcast awareness to other clients
    const encoder = encoding.createEncoder();
    encoding.writeVarUint(encoder, messageAwareness);
    encoding.writeVarString(encoder, roomName);
    encoding.writeVarUint8Array(encoder, awarenessProtocol.encodeAwarenessUpdate(room.awareness, [parseInt(client.id)]));
    
    const message = encoding.toUint8Array(encoder);
    room.clients.forEach(otherClient => {
      if (otherClient !== client && otherClient.ws.readyState === 1) {
        otherClient.ws.send(message);
      }
    });

    room.lastActivity = Date.now();
  }

  private async handleAuthMessage(client: ConnectedClient, decoder: any): Promise<void> {
    const token = decoding.readVarString(decoder);
    // TODO: Implement proper authentication
    client.userId = token; // Simplified for now
    
    logger.info({ clientId: client.id, userId: client.userId }, 'Client authenticated');
  }

  private async handlePresenceMessage(client: ConnectedClient, decoder: any): Promise<void> {
    const roomName = decoding.readVarString(decoder);
    const presenceData = JSON.parse(decoding.readVarString(decoder));
    
    const room = this.rooms.get(roomName);
    if (!room || !client.rooms.has(roomName)) {
      return;
    }

    // Update awareness with presence data
    room.awareness.setLocalStateField('presence', presenceData);
    
    // Broadcast to other clients
    const encoder = encoding.createEncoder();
    encoding.writeVarUint(encoder, messagePresence);
    encoding.writeVarString(encoder, roomName);
    encoding.writeVarString(encoder, JSON.stringify({
      clientId: client.id,
      userId: client.userId,
      ...presenceData
    }));
    
    const message = encoding.toUint8Array(encoder);
    room.clients.forEach(otherClient => {
      if (otherClient !== client && otherClient.ws.readyState === 1) {
        otherClient.ws.send(message);
      }
    });
  }

  private handleDisconnect(client: ConnectedClient): void {
    logger.info({ clientId: client.id }, 'Client disconnected');
    
    // Remove from all rooms
    client.rooms.forEach(roomName => {
      const room = this.rooms.get(roomName);
      if (room) {
        room.clients.delete(client);
        
        // Remove from awareness
        room.awareness.removeAwarenessStates([parseInt(client.id)], client);
        
        // Broadcast awareness update
        const encoder = encoding.createEncoder();
        encoding.writeVarUint(encoder, messageAwareness);
        encoding.writeVarString(encoder, roomName);
        encoding.writeVarUint8Array(encoder, awarenessProtocol.encodeAwarenessUpdate(room.awareness, [parseInt(client.id)]));
        
        const message = encoding.toUint8Array(encoder);
        room.clients.forEach(otherClient => {
          if (otherClient.ws.readyState === 1) {
            otherClient.ws.send(message);
          }
        });
        
        // Clean up empty rooms
        if (room.clients.size === 0) {
          this.scheduleRoomCleanup(roomName);
        }
      }
    });

    this.clients.delete(client.id);
    metrics.decrementActiveConnections();
  }

  private async getOrCreateRoom(roomName: string): Promise<Room> {
    let room = this.rooms.get(roomName);
    
    if (!room) {
      // Create mutex for this room if it doesn't exist
      if (!this.mutexes.has(roomName)) {
        this.mutexes.set(roomName, mutex.createMutex());
      }
      
      const roomMutex = this.mutexes.get(roomName)!;
      
      await mutex.lock(roomMutex, async () => {
        // Double-check pattern
        room = this.rooms.get(roomName);
        if (room) return;

        logger.info({ roomName }, 'Creating new room');
        
        const doc = new Y.Doc();
        const awareness = new awarenessProtocol.Awareness(doc);
        const persistenceKey = `room:${roomName}`;
        
        // Load from event store
        await this.loadRoomFromEventStore(doc, persistenceKey);
        
        // Set up persistence
        doc.on('update', async (update: Uint8Array) => {
          await this.persistUpdate(persistenceKey, update);
        });

        room = {
          name: roomName,
          doc,
          awareness,
          clients: new Set(),
          lastActivity: Date.now(),
          persistenceKey
        };

        this.rooms.set(roomName, room);
        metrics.incrementRoomCount();
      });
    }

    return room!;
  }

  private async loadRoomFromEventStore(doc: Y.Doc, persistenceKey: string): Promise<void> {
    try {
      // First try to load from snapshot
      const snapshot = await this.eventStore.getLatestSnapshot(persistenceKey);
      if (snapshot) {
        const update = new Uint8Array(snapshot.data);
        Y.applyUpdate(doc, update);
        logger.info({ persistenceKey }, 'Loaded room from snapshot');
      }

      // Then load any newer events
      const events = await this.eventStore.getEvents(persistenceKey, snapshot?.version || 0);
      for (const event of events) {
        if (event.event_type === 'yjs_update') {
          const update = new Uint8Array(Buffer.from(event.data.update, 'base64'));
          Y.applyUpdate(doc, update);
        }
      }
      
      if (events.length > 0) {
        logger.info({ persistenceKey, eventCount: events.length }, 'Loaded room events');
      }
    } catch (error) {
      logger.error({ error, persistenceKey }, 'Failed to load room from event store');
    }
  }

  private async persistUpdate(persistenceKey: string, update: Uint8Array): Promise<void> {
    try {
      const event = {
        stream_id: persistenceKey,
        event_type: 'yjs_update',
        data: {
          update: Buffer.from(update).toString('base64'),
          timestamp: Date.now()
        },
        metadata: {
          service: 'collab-engine',
          version: '1.0.0'
        }
      };

      await this.eventStore.appendEvent(event);
      metrics.incrementUpdatesPersisted();
    } catch (error) {
      logger.error({ error, persistenceKey }, 'Failed to persist update');
      metrics.incrementErrorCount();
    }
  }

  private scheduleRoomCleanup(roomName: string): void {
    // Clean up room after 5 minutes of inactivity
    setTimeout(() => {
      const room = this.rooms.get(roomName);
      if (room && room.clients.size === 0 && Date.now() - room.lastActivity > 5 * 60 * 1000) {
        logger.info({ roomName }, 'Cleaning up inactive room');
        this.rooms.delete(roomName);
        this.mutexes.delete(roomName);
        metrics.decrementRoomCount();
      }
    }, 5 * 60 * 1000);
  }

  private sendSync(client: ConnectedClient, encoder: any): void {
    if (encoding.length(encoder) > 1) {
      client.ws.send(encoding.toUint8Array(encoder));
    }
  }

  async start(): Promise<void> {
    // Initialize Redis
    this.redis = createClient({ url: config.redisUrl });
    this.redis.on('error', (err: any) => logger.error({ err }, 'Redis error'));
    await this.redis.connect();

    // Start server
    this.server.listen(config.port, () => {
      logger.info({ port: config.port }, 'Collaboration server started');
    });

    // Periodic cleanup and metrics
    setInterval(() => {
      this.updateMetrics();
    }, 30000); // Every 30 seconds
  }

  private updateMetrics(): void {
    metrics.setRoomCount(this.rooms.size);
    metrics.setClientCount(this.clients.size);
    
    // Memory usage
    const memUsage = process.memoryUsage();
    metrics.setMemoryUsage(memUsage.heapUsed);
    
    logger.debug({
      rooms: this.rooms.size,
      clients: this.clients.size,
      memoryMB: Math.round(memUsage.heapUsed / 1024 / 1024)
    }, 'Server metrics');
  }

  async stop(): Promise<void> {
    logger.info('Shutting down collaboration server');
    
    // Close all client connections
    this.clients.forEach(client => {
      client.ws.close();
    });

    // Close WebSocket server
    this.wss.close();

    // Close Redis connection
    if (this.redis) {
      await this.redis.quit();
    }

    // Close HTTP server
    this.server.close();
  }
}

// Initialize telemetry
initTelemetry();

// Create and start server
const server = new CollaborationServer();

process.on('SIGINT', async () => {
  logger.info('Received SIGINT, shutting down gracefully');
  await server.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('Received SIGTERM, shutting down gracefully');
  await server.stop();
  process.exit(0);
});

server.start().catch((error) => {
  logger.error({ error }, 'Failed to start server');
  process.exit(1);
});
