"""
Standalone crawler runner — run this to populate the database.
Usage: python run_crawler.py [--sections all|regulations|circulars|...]
"""
import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    parser = argparse.ArgumentParser(description="IRDAI Website Crawler")
    parser.add_argument("--sections", nargs="+", default=["all"],
                        help="Sections to crawl (default: all)")
    parser.add_argument("--no-rebuild", action="store_true",
                        help="Skip rebuilding vector index after crawl")
    args = parser.parse_args()

    from crawler import IRDAICrawler, IRDAI_SECTIONS

    if "all" in args.sections:
        sections = IRDAI_SECTIONS
    else:
        sections = [s for s in IRDAI_SECTIONS if s.split("/")[-1] in args.sections]

    print(f"🕷️  Starting IRDAI crawler for {len(sections)} section(s)...")
    crawler = IRDAICrawler()
    crawler.run(sections=sections)

    if not args.no_rebuild:
        print("🔧 Building vector index...")
        from rag_pipeline import rebuild_vector_store
        vs = rebuild_vector_store()
        print(f"✅ Index built: {vs.stats['total_vectors']:,} vectors from {len(vs.stats['sections'])} sections")

    print("\n🚀 Run the app with: streamlit run app.py")

if __name__ == "__main__":
    main()
