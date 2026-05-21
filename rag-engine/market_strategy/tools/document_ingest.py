"""
文档入库工具
将市场相关文档（PDF/Word/TXT）向量化并存入向量数据库
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from document_parser.pdf_parser import PDFParser
from document_parser.word_parser import WordParser
from chunker.text_chunker import TextChunker
from embedding.embedding_service import EmbeddingService
from retrieval.vector_store import insert_chunk, insert_document


class MarketDocIngestor:
    """
    市场文档入库器

    支持文档类型：PDF, Word, TXT
    自动提取元数据并向量化存储
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        batch_size: int = 100
    ):
        self.pdf_parser = PDFParser()
        self.word_parser = WordParser()
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embed_service = EmbeddingService()
        self.batch_size = batch_size

    def ingest_file(
        self,
        file_path: str,
        source: str,
        brand: str = None,
        category: str = "行业报告",
        car_model: str = None,
        publish_date: str = None,
        metadata: Dict = None
    ) -> Dict:
        """
        入库单个文档

        Args:
            file_path: 文件路径
            source: 来源（如：乘联会、中汽协）
            brand: 相关品牌
            category: 文档类别
            car_model: 相关车型
            publish_date: 发布日期
            metadata: 其他元数据

        Returns:
            入库结果
        """
        path = Path(file_path)

        if not path.exists():
            return {"success": False, "error": f"文件不存在: {file_path}"}

        try:
            # 1. 解析文档
            print(f"正在解析: {file_path}")
            pages = self._parse_document(path)

            if not pages:
                return {"success": False, "error": "文档解析失败，无内容"}

            # 合并所有页面文本
            full_text = "\n\n".join([p.get("text", "") for p in pages])

            # 2. 分块
            print(f"正在分块，共 {len(full_text)} 字符")
            chunks = self.chunker.split_text(full_text)

            # 3. 创建文档记录
            doc_id = insert_document(
                file_name=path.name,
                source=source,
                brand=brand,
                category=category
            )

            # 4. 向量化并入库
            print(f"正在向量化 {len(chunks)} 个块...")
            total_chunks = len(chunks)

            for i in range(0, total_chunks, self.batch_size):
                batch = chunks[i:i + self.batch_size]
                batch_texts = [chunk["text"] for chunk in batch]
                batch_indices = [chunk["chunk_index"] for chunk in batch]

                # 批量 embedding
                embeddings = self.embed_service.embed_documents(batch_texts)

                # 批量入库
                for j, (text, embedding, idx) in enumerate(zip(batch_texts, embeddings, batch_indices)):
                    chunk_meta = {
                        "source": source,
                        "brand": brand,
                        "category": category,
                        "car_model": car_model,
                        "publish_date": publish_date,
                        "file_name": path.name,
                        "page_number": batch[j].get("page_number", 1)
                    }
                    if metadata:
                        chunk_meta.update(metadata)

                    insert_chunk(
                        document_id=doc_id,
                        content=text,
                        embedding=embedding,
                        chunk_index=idx,
                        metadata=chunk_meta
                    )

                print(f"  已处理 {min(i + self.batch_size, total_chunks)}/{total_chunks}")

            return {
                "success": True,
                "file_name": path.name,
                "document_id": doc_id,
                "total_pages": len(pages),
                "total_chunks": total_chunks
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_document(self, path: Path) -> List[Dict]:
        """解析文档"""
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return self.pdf_parser.parse(str(path))
        elif suffix in [".doc", ".docx"]:
            return [{"page": 1, "text": self.word_parser.parse(str(path))}]
        elif suffix == ".txt":
            with open(path, 'r', encoding='utf-8') as f:
                return [{"page": 1, "text": f.read()}]
        else:
            raise ValueError(f"不支持的文档格式: {suffix}")

    def ingest_directory(
        self,
        dir_path: str,
        source: str,
        category: str = "行业报告",
        pattern: str = "*.pdf"
    ) -> List[Dict]:
        """
        批量入库目录下所有匹配文件

        Args:
            dir_path: 目录路径
            source: 来源
            category: 文档类别
            pattern: 文件匹配模式

        Returns:
            入库结果列表
        """
        path = Path(dir_path)
        if not path.is_dir():
            return [{"success": False, "error": f"目录不存在: {dir_path}"}]

        results = []
        files = list(path.glob(pattern))

        print(f"找到 {len(files)} 个文件")

        for file_path in files:
            print(f"\n处理文件: {file_path.name}")
            result = self.ingest_file(
                file_path=str(file_path),
                source=source,
                category=category
            )
            results.append(result)

        return results


def main():
    parser = argparse.ArgumentParser(description='市场文档入库工具')
    parser.add_argument('--file', type=str, help='单个文件路径')
    parser.add_argument('--dir', type=str, help='批量入库目录')
    parser.add_argument('--source', type=str, required=True, help='来源（如：乘联会）')
    parser.add_argument('--brand', type=str, help='相关品牌')
    parser.add_argument('--category', type=str, default='行业报告',
                       help='文档类别')
    parser.add_argument('--pattern', type=str, default='*.pdf',
                       help='文件匹配模式')
    parser.add_argument('--chunk_size', type=int, default=500,
                       help='分块大小')
    parser.add_argument('--batch_size', type=int, default=100,
                       help='批量入库大小')

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("必须指定 --file 或 --dir")

    ingestor = MarketDocIngestor(
        chunk_size=args.chunk_size,
        batch_size=args.batch_size
    )

    try:
        if args.file:
            result = ingestor.ingest_file(
                file_path=args.file,
                source=args.source,
                brand=args.brand,
                category=args.category
            )
            print("\n入库结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            results = ingestor.ingest_directory(
                dir_path=args.dir,
                source=args.source,
                category=args.category,
                pattern=args.pattern
            )
            print("\n批量入库结果:")
            success_count = sum(1 for r in results if r.get("success"))
            print(f"成功: {success_count}/{len(results)}")
            for r in results:
                status = "✅" if r.get("success") else "❌"
                print(f"  {status} {r.get('file_name', 'N/A')}: {r.get('error', 'OK')}")

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
