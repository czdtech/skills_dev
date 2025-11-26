import { describe, it, expect } from 'vitest';
import { add, multiply } from './calculator';

describe('Calculator Integration', () => {
    it('should perform complex calculations', () => {
        // (2 + 3) * 4 = 20
        const sum = add(2, 3);
        const result = multiply(sum, 4);
        expect(result).toBe(20);
    });
});
