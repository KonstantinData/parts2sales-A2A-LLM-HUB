from prefect import flow, task

@task
def ingest_articles(): pass

@task
def build_feature_prompt(): pass

@task
def prompt_quality(): pass

@flow
def main():
    data = ingest_articles()
    prompt = build_feature_prompt()
    score = prompt_quality()
    # usw.

if __name__ == "__main__":
    main()
