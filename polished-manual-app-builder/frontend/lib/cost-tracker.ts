export class CostTracker {
  private cost = 0;
  private cap: number;
  constructor(cap: number) {
    this.cap = cap;
  }
  add(amount: number) {
    if (this.cost + amount > this.cap) throw new Error('Cap exceeded');
    this.cost += amount;
  }
  total() {
    return this.cost;
  }
}
