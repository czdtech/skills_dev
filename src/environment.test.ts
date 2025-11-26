import { describe, it, expect } from 'vitest';

describe('Environment', () => {
    it('should have correct NODE_ENV', () => {
        // 故意写错以触发 RED 阶段
        expect(process.env.NODE_ENV).toBe('test');
    });
});
