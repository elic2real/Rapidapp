export interface EventStoreEvent {
  stream_id: string;
  event_type: string;
  data: any;
  metadata?: any;
  expected_version?: number;
}

export interface EventStoreResponse {
  id: string;
  stream_id: string;
  event_type: string;
  data: any;
  metadata?: any;
  version: number;
  created_at: string;
}

export interface Snapshot {
  stream_id: string;
  version: number;
  data: any;
}

export class EventStoreClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, ''); // Remove trailing slashes
  }

  async appendEvent(event: EventStoreEvent): Promise<EventStoreResponse> {
    const response = await fetch(`${this.baseUrl}/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(event),
    });

    if (!response.ok) {
      throw new Error(`Failed to append event: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getEvents(streamId: string, fromVersion = 0, limit = 100): Promise<EventStoreResponse[]> {
    const params = new URLSearchParams({
      from_version: fromVersion.toString(),
      limit: limit.toString(),
    });

    const response = await fetch(`${this.baseUrl}/streams/${encodeURIComponent(streamId)}/events?${params}`);

    if (!response.ok) {
      throw new Error(`Failed to get events: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async createSnapshot(streamId: string, version: number, data: any): Promise<void> {
    const response = await fetch(`${this.baseUrl}/snapshots`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stream_id: streamId,
        version,
        data,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create snapshot: ${response.status} ${response.statusText}`);
    }
  }

  async getLatestSnapshot(streamId: string): Promise<Snapshot | null> {
    const response = await fetch(`${this.baseUrl}/snapshots/${encodeURIComponent(streamId)}/latest`);

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`Failed to get snapshot: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data ? { stream_id: streamId, version: 0, data } : null;
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
