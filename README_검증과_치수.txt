실제 집 영상 기반 3D 재구성

자료: 사용자가 제공한 21.32초, 720×1280 세로 영상
제작: Blender 4.3.2, Cycles CPU 렌더링

포함
- 편집 가능한 Home_Reconstruction.blend
- 실제 Blender 장면에서 렌더링한 4개 시점 이미지
- 교환용 Home_Reconstruction.fbx, Home_Reconstruction.glb
- 재생성용 build_home.py, furnishings.py
- Unreal_Import_Kit: 가져오기용 프로젝트 틀과 스크립트. Unreal 실행 검증 전

치수와 신뢰도
실측, 카메라 내부 보정값, 확인 가능한 제품 모델명이 없는 영상이므로 측량 수준의 정확도를 주장하지 않습니다. 영상에 보이는 사물의 통상 규격과 상대 비율을 교차 비교했습니다.
- 침대: SS 기준 1.10×2.00m 가정. 실물 규격 미확인
- 세탁기: 폭0.60m, 높이0.83m. 소형 전면투입형 일반 규격을 기준으로 추정
- 주방 하부장: 깊이0.60m, 작업대 높이 약0.90m
- 주실: 폭2.70m×길이3.40m, 천장높이2.50m 잠정 모델값
- 폭은 침대1.10m+벽면가구깊이0.60m+통로 약1m의 구성으로 조정
- 욕실 외곽, 현관 깊이와 가려진 벽체는 오차가 큰 추정. 배관·벽두께·문 여닫힘 치수 미검증
- 영상에 다락이나 계단이 확인되지 않아 추가하지 않음

관찰과 모델링
노란 붙박이장, 모니터와 운전대가 있는 책상, 흰 냉장고, 노란 주방 수납장, 세탁기, 개수대, 현관, 욕실, 회색 침구와 연노란 몸베개, 커튼, 창가 탁자, 빨래건조대의 보이는 배치·색·형태를 근거로 제작했습니다. 포장지 글자, 책 제목, 개인 물품의 작은 인쇄 내용은 재현하지 않았습니다. 숨어 있는 면, 옷의 주름과 잡동사니의 개별 형태는 근사치입니다.

중요한 한계
이 파일은 영상의 3D 해석 모델입니다. 사진측량으로 추출한 고정밀 스캔이나 측량도면이 아닙니다. 공사·구매·가구 주문 전에는 실측이 필요합니다.
Blender 원본이 재질과 조명의 기준입니다. FBX/glTF에서는 절차적 목재·섬유 재질의 일부가 단색으로 바뀔 수 있으며 area light는 glTF에서 누락됩니다.
Unreal Engine은 제작 환경에 설치되어 있지 않아 실행, .umap 생성, Lumen 화면 검증, 플레이 가능한 빌드를 완료하지 못했습니다. Unreal_Import_Kit은 이를 숨기지 않고 이후 가져오기를 위한 파일만 제공합니다. Blender 렌더를 Unreal 렌더로 표기하지 않습니다.

일반 규격 비교에 사용한 제조사 자료
제품을 식별한 것이 아니라 영상 비율을 확인하기 위한 비교 기준입니다.
- IKEA GUNDE: 폭41/깊이45/높이78cm, 좌면높이45cm
  https://www.ikea.com/ie/en/p/gunde-folding-chair-black-00217797/
- Samsung 전면투입 세탁기 예시: 폭600/높이850/깊이550mm
  https://www.samsung.com/latin_en/washers-and-dryers/washing-machines/ww6000t-front-loading-eco-bubble-ai-control-super-speed-11-5kg-white-ww11b6900aw-ed/
- IKEA LAGKAPTEN/ALEX 예시: 탁자높이73cm 비교
  https://www.ikea.com/sg/en/p/lagkapten-alex-desk-white-s79521436/
- SONOSEASON SS 침대 규격 예시: 1100×2000mm
  https://www.sonoseason.com/static/images/download/2023_sonoseason_sales_.pdf

오차 해석
주실 폭은 약2.3~2.7m, 다른 방향은 약2.7~3.4m를 검토하는 작업 범위입니다. 이 범위는 통계적 신뢰구간이 아닙니다. 가려진 바닥·벽과 렌즈 왜곡 때문에 실제 치수는 범위 밖일 수 있습니다. 최종 모델은 렌더 구도와 가구 배치가 일치하도록 2.70×3.40m를 택한 한 가지 해석입니다.
