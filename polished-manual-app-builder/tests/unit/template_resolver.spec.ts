import { describe, it, expect } from 'vitest';
import { resolveTemplate } from '../../frontend/template-engine';

describe('TemplateResolver', () => {
  it('should resolve correct template for React CRUD', () => {
    const template = resolveTemplate('react', 'crud');
    expect(template).toMatch(/react/i);
    expect(template).toMatch(/crud/i);
  });
});
