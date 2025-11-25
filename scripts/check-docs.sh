#!/bin/bash
echo "=== 📋 文档维护检查 ==="
echo ""

echo "1️⃣ 检查元数据完整性..."
missing_meta=$(grep -L "最后更新" docs/**/*.md 2>/dev/null)
if [ -z "$missing_meta" ]; then
    echo "   ✅ 所有文档都有更新日期"
else
    echo "   ⚠️  缺少元数据的文档:"
    echo "$missing_meta" | sed 's/^/      /'
fi
echo ""

echo "2️⃣ 检查文档结构..."
echo "   文档总数: $(find docs/ -name '*.md' | wc -l)"
echo "   - architecture/: $(find docs/architecture/ -name '*.md' 2>/dev/null | wc -l)"
echo "   - integration/:  $(find docs/integration/ -name '*.md' 2>/dev/null | wc -l)"
echo "   - reports/:      $(find docs/reports/ -name '*.md' 2>/dev/null | wc -l)"
echo ""

echo "3️⃣ 检查归档目录..."
old_files=$(find .archive/ -type f -mtime +90 2>/dev/null | wc -l)
echo "   超过90天的归档文件: $old_files"
if [ "$old_files" -gt 0 ]; then
    echo "   �� 建议: 可以清理这些旧文件"
fi
echo ""

echo "4️⃣ 文档目录树..."
tree docs/ -L 2 -I 'node_modules|.git' 2>/dev/null || find docs/ -maxdepth 2 -type f -name '*.md' | sort
echo ""

echo "✅ 检查完成!"
