import sys

sys.path.append("../")
import argparse
import os

from huggingface_hub import HfApi, login

from app.common.logger import logger


def main(args):
    model_dir = args.model_dir
    repo_id = args.repo_id

    # 모델 디렉토리 존재 확인
    if not os.path.exists(model_dir):
        logger.error(f"Error: Model directory '{model_dir}' not found.")
        logger.error("Please run 'merge_for_vllm.py' first.")
        return

    # 토큰 처리
    token = os.getenv("HF_TOKEN")
    if token:
        login(token=token)
        logger.info("Logged in with provided token.")

    api = HfApi()

    try:
        # 저장소 생성 (존재하지 않을 경우)
        # private 옵션에 따라 공개/비공개 결정
        api.create_repo(repo_id=repo_id, private=args.private, exist_ok=True)
        visibility = "Private" if args.private else "Public"
        logger.info(f"Repository '{repo_id}' ready ({visibility}).")

        # 폴더 업로드
        logger.info(f"Uploading files from '{model_dir}' to '{repo_id}'...")
        api.upload_folder(
            folder_path=model_dir,
            repo_id=repo_id,
            repo_type="model",
            ignore_patterns=[".git", ".DS_Store", "__pycache__"],
        )
        logger.info(f"Successfully uploaded model to: https://huggingface.co/{repo_id}")

    except Exception as e:
        logger.error(f"Failed to upload: {e}")
        logger.error("Please check your token permissions and repository name.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload merged model to Hugging Face Hub"
    )
    parser.add_argument(
        "--repo_id",
        type=str,
        default="Coxwave/vllm_model",
        help="Hugging Face Repository ID (e.g., username/model-name)",
    )
    parser.add_argument(
        "--model_dir",
        type=str,
        default="vllm_model",
        help="Path to the model directory (default: vllm_model)",
    )
    parser.add_argument(
        "--private", action="store_true", help="Make the repository private"
    )

    args = parser.parse_args()
    main(args)
