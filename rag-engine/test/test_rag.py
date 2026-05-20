from pipeline.rag_pipeline import RAGPipeline


pipeline = RAGPipeline()

# pipeline.ingest_pdf(
#     "YU7配件目录.pdf",
#     source="Yu7配件目录",
#     brand="小米",
#     category="配件目录"
# )

# pipeline.ingest_pdf(
#     "仰望U8 配件目录图册.pdf",
#     source="仰望U8配件目录",
#     brand="仰望U8",
#     category="配件目录"
# )

# pipeline.ingest_pdf(
#     "理想L9零件手册.pdf",
#     source="理想L9零件手册",
#     brand="理想L9",
#     category="零件手册"
# )

# pipeline.ingest_pdf(
#     "tesla.pdf",
#     source="tesla质保",
#     brand="tesla",
#     category="质保手册"
# )

pipeline.ingest_pdf(
    file_path="tesla.pdf",
    source="Tesla",
    brand="Tesla",
    category="电池",
    car_model="Model Y",
    publish_date="2025-12-01"
)

results = pipeline.search(
    "model Y 电池质保期"
)

print(results)