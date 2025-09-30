interface MetricsData {
  activeConnections: number;
  roomCount: number;
  clientCount: number;
  updatesPersisted: number;
  roomJoins: number;
  errorCount: number;
  memoryUsage: number;
}

class Metrics {
  private data: MetricsData = {
    activeConnections: 0,
    roomCount: 0,
    clientCount: 0,
    updatesPersisted: 0,
    roomJoins: 0,
    errorCount: 0,
    memoryUsage: 0,
  };

  incrementActiveConnections(): void {
    this.data.activeConnections++;
  }

  decrementActiveConnections(): void {
    this.data.activeConnections = Math.max(0, this.data.activeConnections - 1);
  }

  incrementRoomCount(): void {
    this.data.roomCount++;
  }

  decrementRoomCount(): void {
    this.data.roomCount = Math.max(0, this.data.roomCount - 1);
  }

  setRoomCount(count: number): void {
    this.data.roomCount = count;
  }

  setClientCount(count: number): void {
    this.data.clientCount = count;
  }

  incrementUpdatesPersisted(): void {
    this.data.updatesPersisted++;
  }

  incrementRoomJoins(): void {
    this.data.roomJoins++;
  }

  incrementErrorCount(): void {
    this.data.errorCount++;
  }

  setMemoryUsage(bytes: number): void {
    this.data.memoryUsage = bytes;
  }

  async getMetrics(): Promise<string> {
    const timestamp = Date.now();
    
    return `
# HELP collab_engine_active_connections Number of active WebSocket connections
# TYPE collab_engine_active_connections gauge
collab_engine_active_connections ${this.data.activeConnections} ${timestamp}

# HELP collab_engine_rooms Number of active rooms
# TYPE collab_engine_rooms gauge
collab_engine_rooms ${this.data.roomCount} ${timestamp}

# HELP collab_engine_clients Number of active clients
# TYPE collab_engine_clients gauge
collab_engine_clients ${this.data.clientCount} ${timestamp}

# HELP collab_engine_updates_persisted_total Total number of updates persisted
# TYPE collab_engine_updates_persisted_total counter
collab_engine_updates_persisted_total ${this.data.updatesPersisted} ${timestamp}

# HELP collab_engine_room_joins_total Total number of room joins
# TYPE collab_engine_room_joins_total counter
collab_engine_room_joins_total ${this.data.roomJoins} ${timestamp}

# HELP collab_engine_errors_total Total number of errors
# TYPE collab_engine_errors_total counter
collab_engine_errors_total ${this.data.errorCount} ${timestamp}

# HELP collab_engine_memory_usage_bytes Memory usage in bytes
# TYPE collab_engine_memory_usage_bytes gauge
collab_engine_memory_usage_bytes ${this.data.memoryUsage} ${timestamp}
`.trim();
  }

  getData(): MetricsData {
    return { ...this.data };
  }
}

export const metrics = new Metrics();
