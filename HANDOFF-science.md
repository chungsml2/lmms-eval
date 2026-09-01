# `science` 브랜치 인수인계 문서

다른 서버에서 이 작업을 이어받기 위한 문서입니다.
저장소: `https://github.com/dalgarak/lmms-eval` (upstream `EvolvingLMMs-Lab/lmms-eval`의 fork)
작업 브랜치: `science`

---

## 1. 이 브랜치가 하는 일

Qwen3.5 계열 모델을 **과학 도메인 멀티모달 벤치마크**로 평가하기 위해,
lmms-eval에 없는 태스크들을 직접 추가한 브랜치입니다.

`science` 고유 커밋은 upstream `main` 위에 얹혀 있고, 주기적으로 `origin/main`을 머지해 최신화합니다.

```
* Merge remote-tracking branch 'origin/main' into science
* Merge remote-tracking branch 'origin/main' into science
* feat: add science-domain benchmark tasks
* MolParse, OpenRxn 기본 테스트 완료
* (upstream main)
```

---

## 2. 새 서버에서 시작하기

### 2.1 클론 & 브랜치

```bash
git clone https://github.com/dalgarak/lmms-eval.git
cd lmms-eval
git checkout science
```

### 2.2 git 신원 설정 (필요)

이 저장소에는 git user 설정이 없습니다. 커밋 전에 한 번 설정하세요.

```bash
git config --local user.name  "dalgarak"
git config --local user.email "20063100+dalgarak@users.noreply.github.com"
```

### 2.3 push 인증

HTTPS remote라 자격증명이 필요합니다. 둘 중 하나:

```bash
# (a) SSH 키를 GitHub 계정에 등록한 경우
git remote set-url origin git@github.com:dalgarak/lmms-eval.git

# (b) PAT 사용
git config --local credential.helper store   # 최초 1회 입력 후 저장
```

### 2.4 환경

기존 작업 서버 기준(참고값):

| 항목 | 값 |
|---|---|
| Python | 3.12.3 (`requires-python >=3.10`) |
| 패키지 매니저 | `uv` 0.9.18 |
| GPU | NVIDIA B200 183GB × 4 |
| 가상환경 | 리포 루트의 `.venv` (uv 관리) |

```bash
uv sync
```

주의할 의존성 (`pyproject.toml`의 `dependencies`에 이 브랜치가 추가한 것):

| 패키지 | 용도 |
|---|---|
| `rouge_score`, `bert_score`, `pymeteor` | sfe 계열 생성 태스크 채점 |
| `causal-conv1d`, `flash-linear-attention` | Qwen3.5 추론 가속 |

- `pymeteor`는 **test.pypi.org**에서 받습니다. `pyproject.toml`의 `[tool.uv.sources]` / `[[tool.uv.index]]` 설정이 이를 담당하니 지우지 마세요.
- Qwen3.5 모델 로딩에는 `transformers>=5.3.0`이 필요합니다 (스크립트 상단 주석 참고).
- upstream이 최근 린터를 black/isort → **ruff**로 교체했습니다. 포맷 관련 커밋 시 참고.

---

## 3. 실행 방법

실행 스크립트는 `examples/models/` 아래 두 개입니다. 같은 내용이고 **GPU만 나눠 쓰는 구조**입니다.

| 스크립트 | GPU | 포트 |
|---|---|---|
| `examples/models/qwen35_science.sh` | 기본(0,1) | 12346 |
| `examples/models/qwen35_science_2.sh` | `CUDA_VISIBLE_DEVICES=2,3` | 12348 |

```bash
bash examples/models/qwen35_science.sh
```

스크립트 안에서 바꿔가며 쓰는 값:

- `TASKS` — 돌릴 태스크. 여러 개는 콤마로 구분 (히스토리가 주석으로 남아 있음)
- `MODEL` — 현재 `Qwen/Qwen3.5-9B`
- `--limit 5` — 스모크 테스트용. 전체 실행 시 주석 처리 (현재 `_2.sh`에만 켜져 있음)
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` — OOM 회피용으로 붙여둔 것

결과는 `./logs/<모델명>/<타임스탬프>_results.json`에 쌓입니다.
**`logs/`는 `.gitignore` 대상이라 커밋되지 않습니다.** 서버를 옮길 때 결과가 필요하면 따로 복사하세요.

---

## 4. 태스크 인벤토리

이 브랜치가 추가한 태스크 목록과 현재 상태입니다.

| 태스크 ID | 데이터 출처 | 채점 방식 | 상태 |
|---|---|---|---|
| `MolParse` | HF `InnovatorLab/MolParse` | LLM judge (API) | ✅ 전체 실행 완료 |
| `OpenRxn` | HF `InnovatorLab/OpenRxn` | LLM judge (API) | ✅ 전체 실행 완료 |
| `EMVista` | HF `InnovatorLab/EMVista` | exact match | ✅ 전체 실행 완료 |
| `rxnbench_vqa_en` / `_zh` | HF `UniParser/RxnBench` (`RxnBench-VQA`) | exact match | ✅ 전체 실행 완료 |
| `rxnbench_vqa` (그룹) | 위 둘 묶음 | — | ⚠️ 그룹 집계 결과가 비어서(`{}`) 나옴. 개별 태스크로 돌리는 중 |
| `msearth_mcq` | HF `MSEarth/MSEarth_MCQ` | accuracy | ✅ 전체 실행 완료 |
| `microvqa` | HF `jmhb/microvqa` | accuracy | ✅ 전체 실행 완료 — **단 구현이 교체됨, 5절 참고** |
| `ProteinLMBench` | HF `tsynbio/ProteinLMBench` (`evaluation`, gated) | accuracy | ⚠️ `--limit 5`만 확인. 전체 실행 미완 |
| `sfe-en` / `sfe-zh` | HF `etri-lirs/SFE` | LLM judge (API) + ROUGE/BERTScore/METEOR | ❌ 미실행 |
| `superchem_en` / `superchem_cn` | 로컬 parquet | — | ❌ 미실행, **데이터 경로 미해결 (6절)** |
| `SmolInstruct` (그룹, 14개 하위 태스크) | 로컬 jsonl | 태스크별 상이 | ❌ 미실행, **데이터 전처리 필요 (6절)** |

`SmolInstruct` 하위 태스크 14종: `smol_forward_synthesis`, `smol_retrosynthesis`, `smol_molecule_captioning`, `smol_molecule_generation`, `smol_name_conversion-{i2f,i2s,s2f,s2i}`, `smol_property_prediction-{esol,lipo,bbbp,clintox,hiv,sider}`

### 참고 baseline (`Qwen/Qwen3.5-9B`, 전체 실행)

이어받는 쪽에서 회귀 여부를 판단할 기준값입니다.

| 태스크 | 지표 | 값 |
|---|---|---|
| `scienceqa` | exact_match | 0.9283 |
| `rxnbench_vqa_en` | exact_match | 0.8807 |
| `rxnbench_vqa_zh` | exact_match | 0.8728 |
| `msearth_mcq` | accuracy | 0.5675 |
| `microvqa` | accuracy | 0.5547 |
| `xlrs-lite` | micro / macro | 0.4455 / 0.4729 |
| `EMVista` | exact_match_accuracy | 0.4389 |
| `OpenRxn` | api_judge_accuracy | 0.2350 |
| `MolParse` | api_judge_accuracy | 0.1295 |

---

## 5. 환경변수

LLM judge를 쓰는 태스크는 환경변수 설정 없이는 점수가 무의미합니다. `.env`는 gitignore 대상이라 저장소에 없으니 **새 서버에서 직접 만들어야 합니다.**

### `MolParse`, `OpenRxn`

| 변수 | 기본값 | 비고 |
|---|---|---|
| `OPENAI_API_KEY` | `"EMPTY"` | |
| `OPENAI_BASE_URL` | `http://localhost:8000/v1` | 기본값이 로컬이라, **judge용 OpenAI 호환 서버(vLLM 등)를 별도로 띄워 쓰던 구조로 보입니다** |
| `OPENAI_MODEL_NAME` | `"default-model"` | |

> ⚠️ 기존 서버에서 어떤 judge 모델/서버를 띄웠는지는 저장소에 기록이 없습니다. 위 세 값을 이전 담당자에게 확인하지 않으면 MolParse/OpenRxn 점수를 그대로 재현할 수 없습니다.

### `sfe-en`, `sfe-zh`

| 변수 | 기본값 |
|---|---|
| `API_TYPE` | `openai` (또는 `azure`) |
| `MODEL_VERSION` | `gpt-4o-2024-08-06` |
| `FILE_NAME` | `sfe_test.json` |
| `OPENAI_API_BASE` / `OPENAI_API_KEY` | `https://api.openai.com/v1` / — |
| `AZURE_ENDPOINT` / `AZURE_API_KEY` | (`API_TYPE=azure`일 때) |

### 공통

| 변수 | 용도 |
|---|---|
| `HF_HOME` | `rxnbench_vqa`가 이미지 캐시 경로 확인에 사용 (기본 `~/.cache/huggingface/`) |
| `HF_TOKEN` | `ProteinLMBench`가 gated 데이터셋이라 `dataset_kwargs.token: True`로 설정됨. HF 로그인 필요 |

---

## 6. 미해결 이슈 / 다음 할 일

우선순위 순입니다.

1. **`SmolInstruct` 데이터 준비** — 각 yaml이 `dataset_path: json` + 상대경로 jsonl(`molecule_captioning.jsonl` 등)을 참조합니다. `lmms_eval/tasks/SmolInstruct/process_data.py`로 생성하는 구조인데, 그 스크립트의 `snapshot_path`가 **빈 문자열**이라 그대로는 동작하지 않습니다. HF 스냅샷 경로를 채우고 실행 → 생성된 `./processed_smol_test_data` 경로를 14개 yaml의 `data_files`에 반영해야 합니다.
2. **`superchem` 데이터 경로 수정** — `dataset_path: "parquet"`인데 `data_files.test`가 `"ZehuaZhao/SUPERChem"`(HF repo id)로 들어가 있습니다. parquet 로더에 repo id를 넘기는 형태라 로컬 parquet 파일 경로로 바꾸거나 `dataset_path`를 HF 방식으로 고쳐야 합니다.
3. **`sfe-en` / `sfe-zh` 첫 실행** — judge API 키 설정 후 `--limit 5`로 스모크 테스트부터.
4. **`ProteinLMBench` 전체 실행** — `--limit 5`(accuracy 0.6)까지만 확인됨.
5. **`rxnbench_vqa` 그룹 집계** — 그룹으로 돌리면 결과가 `{}`로 비어 나옵니다. 그룹 aggregation 설정 확인 필요. 당장은 `rxnbench_vqa_en`, `rxnbench_vqa_zh`를 개별로 돌리면 됩니다.

---

## 7. 인수인계 시 반드시 알아야 할 함정

### 7.1 `microvqa` 구현이 upstream 것으로 교체됨

upstream이 `microvqa`를 독립적으로 추가하면서 add/add 충돌이 났고, **upstream 버전을 채택**했습니다. 두 구현은 평가 프로토콜이 다릅니다.

| | 현재(upstream) | 이전(science) |
|---|---|---|
| 선택지 표기 | 숫자 `(1) (2)` | 알파벳 `(A) (B)` |
| 정답 파싱 | 숫자만 | 숫자·알파벳 + 단일문자 fallback |
| 모드 | 단일 | `stage1` / `noimage` / `noimage_v2` / `noimage_v3` |
| 샘플링 | temp 1.0, do_sample, seed 0 | temp 0.0 greedy |

→ **머지 이전에 뽑은 microvqa 결과와 이후 결과를 직접 비교하면 안 됩니다.** 위 baseline 표의 0.5547은 교체 이전 값입니다. 이전 구현이 필요하면 `git show cb518730:lmms_eval/tasks/microvqa/utils.py`로 꺼낼 수 있습니다.

### 7.2 Qwen3-VL pixel budget 계산 변경

upstream PR #1490, #1502가 Qwen3-VL의 visual token budget 계산을 수정했습니다. 실행 스크립트가 `MAX_PIXELS=$((2048*32*32))`, `MIN_PIXELS=$((256*32*32))`를 넘기고 있어, **적용되는 실제 visual token 수가 이전 실행과 달라질 수 있습니다.**

사용 중인 모델 로더는 `--model qwen3_5`이고 수정된 파일은 `lmms_eval/models/simple/qwen3_vl.py`라 서로 다른 파일이지만, 공유 로직 여부는 실제 실행으로 확인하는 것이 확실합니다.

### 7.3 결과 로그는 저장소에 없음

`logs/`가 gitignore 대상입니다. 위 baseline 표가 남아 있는 유일한 기록이므로, 서버 이전 시 원본이 필요하면 `logs/` 디렉터리를 별도로 옮기세요.

---

## 8. upstream 최신화 절차

정기적으로 이렇게 따라잡습니다.

```bash
git fetch origin
git branch -f main origin/main        # 로컬 main은 항상 origin/main과 동일하게 유지
git checkout science
git merge origin/main                 # rebase 아님 — 이미 push된 브랜치이므로
# 충돌 해결 후
git commit
git push origin science
```

지금까지 충돌이 난 곳은 `lmms_eval/tasks/microvqa/`뿐입니다. `pyproject.toml`은 매번 자동 병합됐지만, 머지 후 이 브랜치가 추가한 의존성이 살아있는지 확인하는 습관을 권합니다.

```bash
grep -E 'pymeteor|rouge_score|bert_score|causal-conv1d|flash-linear-attention' pyproject.toml
```
