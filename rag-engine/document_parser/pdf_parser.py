import fitz
import re


class PDFParser:

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清洗 PDF 文本
        """

        # 去多余空白
        text = re.sub(r"\s+", " ", text)

        # 去连续空行
        text = re.sub(r"\n+", "\n", text)

        # 修复中文换行断裂
        text = re.sub(r"([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])", r"\1\2", text)

        return text.strip()

    @staticmethod
    def parse(file_path: str) -> str:
        """
        解析 PDF 文件
        """

        doc = fitz.open(file_path)

        texts = []

        for page in doc:

            text = page.get_text()

            if text:

                clean_text = PDFParser.clean_text(text)

                texts.append(clean_text)

        return "\n".join(texts)