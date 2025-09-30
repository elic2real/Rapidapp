import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import * as Y from 'yjs';
import * as awarenessProtocol from 'y-protocols/awareness';

describe('Yjs Convergence Tests', () => {
  let doc1: Y.Doc;
  let doc2: Y.Doc;
  let awareness1: awarenessProtocol.Awareness;
  let awareness2: awarenessProtocol.Awareness;

  beforeEach(() => {
    doc1 = new Y.Doc();
    doc2 = new Y.Doc();
    awareness1 = new awarenessProtocol.Awareness(doc1);
    awareness2 = new awarenessProtocol.Awareness(doc2);
  });

  afterEach(() => {
    doc1.destroy();
    doc2.destroy();
  });

  it('should converge text edits from two clients', () => {
    // Setup shared text objects
    const text1 = doc1.getText('content');
    const text2 = doc2.getText('content');

    // Client 1 inserts "Hello"
    text1.insert(0, 'Hello');
    
    // Apply update from doc1 to doc2
    const update1 = Y.encodeStateAsUpdate(doc1);
    Y.applyUpdate(doc2, update1);

    // Client 2 inserts " World" at the end
    text2.insert(5, ' World');
    
    // Apply update from doc2 to doc1
    const update2 = Y.encodeStateAsUpdate(doc2);
    Y.applyUpdate(doc1, update2);

    // Both documents should converge to "Hello World"
    expect(text1.toString()).toBe('Hello World');
    expect(text2.toString()).toBe('Hello World');
  });

  it('should handle concurrent edits correctly', () => {
    const text1 = doc1.getText('content');
    const text2 = doc2.getText('content');

    // Both start with "Hello"
    text1.insert(0, 'Hello');
    const initialUpdate = Y.encodeStateAsUpdate(doc1);
    Y.applyUpdate(doc2, initialUpdate);

    // Client 1 adds " there" at position 5
    text1.insert(5, ' there');
    
    // Client 2 adds " World" at position 5 (before syncing with client 1)
    text2.insert(5, ' World');

    // Sync updates
    const update1 = Y.encodeStateAsUpdate(doc1);
    const update2 = Y.encodeStateAsUpdate(doc2);
    
    Y.applyUpdate(doc2, update1);
    Y.applyUpdate(doc1, update2);

    // Both should converge to the same state
    expect(text1.toString()).toBe(text2.toString());
    
    // The result should contain both insertions
    const result = text1.toString();
    expect(result).toContain('there');
    expect(result).toContain('World');
  });

  it('should handle deletions correctly', () => {
    const text1 = doc1.getText('content');
    const text2 = doc2.getText('content');

    // Start with "Hello World"
    text1.insert(0, 'Hello World');
    const initialUpdate = Y.encodeStateAsUpdate(doc1);
    Y.applyUpdate(doc2, initialUpdate);

    // Client 1 deletes "Hello "
    text1.delete(0, 6);
    
    // Client 2 deletes " World"
    text2.delete(5, 6);

    // Sync updates
    const update1 = Y.encodeStateAsUpdate(doc1);
    const update2 = Y.encodeStateAsUpdate(doc2);
    
    Y.applyUpdate(doc2, update1);
    Y.applyUpdate(doc1, update2);

    // Both should converge
    expect(text1.toString()).toBe(text2.toString());
  });

  it('should handle offline scenarios with conflict resolution', () => {
    const text1 = doc1.getText('content');
    const text2 = doc2.getText('content');

    // Initial sync
    text1.insert(0, 'Original text');
    const initialUpdate = Y.encodeStateAsUpdate(doc1);
    Y.applyUpdate(doc2, initialUpdate);

    // Simulate offline: both clients make changes without syncing
    
    // Client 1 offline changes
    text1.insert(8, ' modified');
    text1.insert(0, 'Updated: ');

    // Client 2 offline changes  
    text2.delete(9, 4); // Delete "text"
    text2.insert(9, 'content');

    // Come back online and sync
    const offlineUpdate1 = Y.encodeStateAsUpdate(doc1);
    const offlineUpdate2 = Y.encodeStateAsUpdate(doc2);
    
    Y.applyUpdate(doc2, offlineUpdate1);
    Y.applyUpdate(doc1, offlineUpdate2);

    // Should converge to a consistent state
    expect(text1.toString()).toBe(text2.toString());
    
    const result = text1.toString();
    expect(result).toContain('Updated:');
    expect(result).toContain('modified');
    expect(result).toContain('content');
  });

  it('should maintain awareness state', () => {
    // Set awareness state for client 1
    awareness1.setLocalStateField('user', {
      name: 'Alice',
      cursor: { line: 1, column: 5 }
    });

    // Encode and apply awareness update
    const awarenessUpdate = awarenessProtocol.encodeAwarenessUpdate(awareness1, [1]);
    awarenessProtocol.applyAwarenessUpdate(awareness2, awarenessUpdate, null);

    // Check awareness state is propagated
    const states = awareness2.getStates();
    expect(states.size).toBe(1);
    
    const userState = states.get(1);
    expect(userState?.user?.name).toBe('Alice');
    expect(userState?.user?.cursor?.line).toBe(1);
  });

  it('should handle maps and arrays', () => {
    const map1 = doc1.getMap('config');
    const map2 = doc2.getMap('config');
    
    const array1 = doc1.getArray('items');
    const array2 = doc2.getArray('items');

    // Client 1 sets map values
    map1.set('theme', 'dark');
    map1.set('fontSize', 14);
    
    // Client 1 adds array items
    array1.push(['item1', 'item2']);

    // Sync to client 2
    const update1 = Y.encodeStateAsUpdate(doc1);
    Y.applyUpdate(doc2, update1);

    // Client 2 modifies map and array
    map2.set('language', 'en');
    array2.push(['item3']);

    // Sync back to client 1
    const update2 = Y.encodeStateAsUpdate(doc2);
    Y.applyUpdate(doc1, update2);

    // Verify convergence
    expect(map1.get('theme')).toBe('dark');
    expect(map1.get('fontSize')).toBe(14);
    expect(map1.get('language')).toBe('en');
    expect(map2.get('theme')).toBe('dark');
    expect(map2.get('fontSize')).toBe(14);
    expect(map2.get('language')).toBe('en');

    expect(array1.toArray()).toEqual(['item1', 'item2', 'item3']);
    expect(array2.toArray()).toEqual(['item1', 'item2', 'item3']);
  });

  it('should handle rapid sequential edits', () => {
    const text1 = doc1.getText('content');
    const text2 = doc2.getText('content');

    // Rapid edits from client 1
    for (let i = 0; i < 10; i++) {
      text1.insert(text1.length, `${i} `);
    }

    // Rapid edits from client 2
    for (let i = 10; i < 20; i++) {
      text2.insert(0, `${i} `);
    }

    // Sync updates
    const update1 = Y.encodeStateAsUpdate(doc1);
    const update2 = Y.encodeStateAsUpdate(doc2);
    
    Y.applyUpdate(doc2, update1);
    Y.applyUpdate(doc1, update2);

    // Should converge
    expect(text1.toString()).toBe(text2.toString());
    
    // Should contain all numbers
    const result = text1.toString();
    for (let i = 0; i < 20; i++) {
      expect(result).toContain(i.toString());
    }
  });

  it('should preserve document state after updates', () => {
    const text1 = doc1.getText('content');
    const text2 = doc2.getText('content');

    // Create initial state
    text1.insert(0, 'Hello World');
    
    // Create state vector before update
    const stateBefore = Y.encodeStateVector(doc1);
    
    // Apply to second document
    const update = Y.encodeStateAsUpdate(doc1);
    Y.applyUpdate(doc2, update);
    
    // Create diff update
    const diff = Y.encodeStateAsUpdate(doc1, stateBefore);
    
    // Verify the diff contains the changes
    expect(diff.length).toBeGreaterThan(0);
    
    // Apply diff to a new document
    const doc3 = new Y.Doc();
    Y.applyUpdate(doc3, diff);
    const text3 = doc3.getText('content');
    
    expect(text3.toString()).toBe('Hello World');
    
    doc3.destroy();
  });
});

describe('Event Store Integration', () => {
  it('should simulate event store persistence and loading', async () => {
    const doc1 = new Y.Doc();
    const text1 = doc1.getText('content');
    
    // Simulate events being persisted
    const events: Uint8Array[] = [];
    
    doc1.on('update', (update: Uint8Array) => {
      events.push(update);
    });

    // Make some changes
    text1.insert(0, 'Hello');
    text1.insert(5, ' World');
    text1.insert(11, '!');

    // Simulate loading from event store
    const doc2 = new Y.Doc();
    const text2 = doc2.getText('content');
    
    // Apply all persisted events
    events.forEach(update => {
      Y.applyUpdate(doc2, update);
    });

    // Should match original
    expect(text2.toString()).toBe('Hello World!');
    
    doc1.destroy();
    doc2.destroy();
  });

  it('should handle snapshot creation and loading', () => {
    const doc1 = new Y.Doc();
    const text1 = doc1.getText('content');
    
    // Create some content
    text1.insert(0, 'This is a long document with lots of content');
    
    // Create snapshot (full state)
    const snapshot = Y.encodeStateAsUpdate(doc1);
    
    // Create new document and load from snapshot
    const doc2 = new Y.Doc();
    Y.applyUpdate(doc2, snapshot);
    const text2 = doc2.getText('content');
    
    expect(text2.toString()).toBe('This is a long document with lots of content');
    
    // Make more changes to original
    text1.insert(0, 'Updated: ');
    
    // Create incremental update
    const incrementalUpdate = Y.encodeStateAsUpdate(doc1, Y.encodeStateVector(doc2));
    
    // Apply incremental to doc2
    Y.applyUpdate(doc2, incrementalUpdate);
    
    expect(text2.toString()).toBe('Updated: This is a long document with lots of content');
    
    doc1.destroy();
    doc2.destroy();
  });
});
