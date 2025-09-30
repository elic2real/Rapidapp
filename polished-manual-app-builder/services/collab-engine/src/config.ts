export const config = {
  port: parseInt(process.env.PORT || '8003'),
  eventStoreUrl: process.env.EVENT_STORE_URL || 'http://localhost:8080',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  jaegerEndpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces',
  logLevel: process.env.LOG_LEVEL || 'info',
  
  // Room configuration
  roomCleanupInterval: parseInt(process.env.ROOM_CLEANUP_INTERVAL || '300000'), // 5 minutes
  maxRoomsPerInstance: parseInt(process.env.MAX_ROOMS_PER_INSTANCE || '1000'),
  maxClientsPerRoom: parseInt(process.env.MAX_CLIENTS_PER_ROOM || '100'),
  
  // Persistence configuration
  snapshotInterval: parseInt(process.env.SNAPSHOT_INTERVAL || '100'), // Every 100 updates
  batchUpdates: process.env.BATCH_UPDATES === 'true',
  batchSize: parseInt(process.env.BATCH_SIZE || '10'),
  batchTimeout: parseInt(process.env.BATCH_TIMEOUT || '1000'), // 1 second
};
