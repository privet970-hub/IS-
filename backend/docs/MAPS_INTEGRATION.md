# Google Maps API Integration Guide

## 개요

IS- 애플리케이션은 Google Maps API를 사용하여 실제 도로 거리와 이동 시간을 계산합니다. 이를 통해 더 정확한 경로 최적화를 제공합니다.

## 기능

### 1. 거리 계산 (Distance Matrix API)
- **설명**: 여러 출발지에서 여러 목적지까지의 거리 계산
- **용도**: 경로 최적화를 위한 거리 행렬 생성
- **모드**: 자동차, 보행, 자전거, 대중교통

### 2. 거리 및 소요시간 (Distance Matrix API)
- **설명**: 두 지점 간 거리와 소요시간 계산
- **용도**: 상세한 경로 정보 제공

### 3. 캐싱
- **설명**: 계산한 거리 데이터를 메모리에 저장
- **효과**: API 호출 횟수 감소 및 응답 속도 개선
- **TTL**: 1시간 (설정 가능)

### 4. Fallback (Haversine Formula)
- **설명**: Google Maps API가 사용 불가능할 때 직선 거리 계산
- **용도**: API 오류 시 서비스 연속성 보장

## 설정

### 1. API 키 발급

Google Cloud Console에서 API 키를 발급받습니다:

```bash
1. https://console.cloud.google.com로 접속
2. 새 프로젝트 생성
3. "Maps" > "Maps API"에서 "Distance Matrix API" 활성화
4. "APIs & Services" > "Credentials"에서 API 키 생성
5. 제한사항 설정 (선택사항): Application restrictions = None, API restrictions = Distance Matrix API
```

### 2. 환경 변수 설정

`.env` 파일에 다음을 추가합니다:

```env
# Google Maps API
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
GOOGLE_MAPS_DISTANCE_MATRIX_CACHE=true
GOOGLE_MAPS_CACHE_TTL=3600
```

### 3. 비용 절감 전략

**예상 비용 (월별)**:
- Distance Matrix API: 요청당 $0.05 (1,000,000 요청 이후 $0.025)
- 100,000 요청/월 = $5,000

**비용 절감 방법**:
1. **캐싱 활성화**: 중복된 거리 계산 방지
   ```python
   GOOGLE_MAPS_DISTANCE_MATRIX_CACHE=true
   GOOGLE_MAPS_CACHE_TTL=3600  # 1시간
   ```

2. **배치 처리**: 대량의 위치를 한 번에 처리
   ```python
   # 좋은 예
   distance_matrix = maps_service.get_distance_matrix(
       origins=all_origins,
       destinations=all_destinations
   )
   
   # 나쁜 예 - 매번 API 호출
   for origin in origins:
       for destination in destinations:
           distance = maps_service.get_distance_and_duration(origin, destination)
   ```

3. **API 키 제한**: 특정 IP 또는 도메인으로만 제한
4. **할당량 설정**: Google Cloud Console에서 월별 할당량 제한 설정

## 사용 방법

### 기본 사용

```python
from app.services.maps_service import MapsService

# MapsService 인스턴스 생성
maps_service = MapsService(api_key="your_api_key")

# 거리 및 소요시간 조회
origin = (37.5665, 126.9780)  # 서울 (위도, 경도)
destination = (37.4979, 127.0276)  # 성남

result = maps_service.get_distance_and_duration(origin, destination)
print(f"거리: {result['distance']} 미터")
print(f"소요시간: {result['duration']} 초")
```

### 거리 행렬 계산

```python
origins = [
    (37.5665, 126.9780),  # 서울
    (37.4979, 127.0276),  # 성남
]
destinations = [
    (35.1796, 129.0756),  # 부산
    (36.8000, 128.5000),  # 대구
]

distance_matrix = maps_service.get_distance_matrix(
    origins=origins,
    destinations=destinations,
    mode="driving"
)

# distance_matrix[i][j] = 원점 i에서 목적지 j까지의 거리 (미터)
```

### 경로 최적화에 통합

```python
from app.services.route_optimizer import RouteOptimizerService

optimizer = RouteOptimizerService()  # Google Maps를 자동으로 사용

result = optimizer.optimize(
    vehicles=vehicles,
    stops=stops,
    start_location=depot,
    time_limit_seconds=30
)
```

## 응답 형식

### get_distance_and_duration 응답

```json
{
    "distance": 25000,  // 미터 단위
    "duration": 1500    // 초 단위
}
```

### get_distance_matrix 응답

```json
[
    [0, 25000, 320000],
    [25000, 0, 300000],
    [320000, 300000, 0]
]
```

## 에러 처리

```python
try:
    result = maps_service.get_distance_and_duration(origin, destination)
except Exception as e:
    print(f"Error: {e}")
    # Haversine 계산으로 자동 대체
```

## 테스트

### 단위 테스트 실행

```bash
# 모든 테스트
pytest tests/test_maps_service.py -v

# 특정 테스트
pytest tests/test_maps_service.py::TestMapsService::test_haversine_distance_calculation -v

# 캐시 테스트
pytest tests/test_maps_service.py::TestDistanceMatrixCache -v
```

### 테스트 케이스

| 테스트 | 설명 |
|--------|------|
| `test_haversine_distance_calculation` | Haversine 거리 계산 검증 |
| `test_haversine_same_point` | 같은 지점 거리 = 0 |
| `test_haversine_distance_matrix` | Haversine 거리 행렬 |
| `test_get_distance_and_duration_with_api` | Google Maps API 호출 |
| `test_get_distance_matrix_with_api` | Google Maps 거리 행렬 |
| `test_get_distance_and_duration_fallback` | API 불가능 시 대체 |
| `test_cache_functionality` | 캐싱 기능 검증 |

## 성능 최적화

### 1. 캐시 설정 최적화

```python
# app/config.py
GOOGLE_MAPS_CACHE_TTL = 3600  # 1시간
# 자주 변하지 않는 경로: 3600 ~ 7200초
# 자주 변하는 경로: 600 ~ 1800초
```

### 2. 배치 크기 최적화

```python
# Google Maps API 제한: 최대 25개 원점 × 25개 목적지 = 625 요소
# 권장: 100~200 요소 이하로 배치 처리

max_batch_size = 150
for i in range(0, len(locations), max_batch_size):
    batch = locations[i:i+max_batch_size]
    distance_matrix = maps_service.get_distance_matrix(
        origins=batch,
        destinations=batch
    )
```

### 3. 동시성 제어

```python
# API 호출 속도 제한 (Quota exceeded 방지)
import asyncio

async def get_multiple_distances(origin_destination_pairs):
    tasks = []
    for origin, destination in origin_destination_pairs:
        tasks.append(
            asyncio.sleep(0.1)  # 100ms 지연
        )
        tasks.append(
            maps_service.get_distance_and_duration(origin, destination)
        )
    return await asyncio.gather(*tasks)
```

## 트러블슈팅

### 1. "API Key not valid" 에러

```python
# 확인사항
1. API 키가 올바르게 설정되었는지 확인
2. .env 파일 로드 여부 확인
3. API 키 활성화 여부 확인 (Google Cloud Console)
4. Distance Matrix API가 활성화되었는지 확인
```

### 2. "ZERO_RESULTS" 에러

```python
# 해결방법
1. 좌표가 올바른 형식인지 확인 (위도, 경도)
2. 좌표가 실제 도로가 있는 위치인지 확인
3. 한국 전역을 벗어난 좌표는 Haversine으로 자동 대체
```

### 3. 과도한 API 호출

```python
# 해결방법
1. 캐싱이 활성화되었는지 확인
2. 캐시 TTL 값 조정
3. 배치 처리 적용
4. API 호출 로그 확인

# 로그 확인
import logging
logging.getLogger("app.services.maps_service").setLevel(logging.DEBUG)
```

## 예제

### 전체 경로 최적화 예제

```python
from app.models.vehicle import Vehicle
from app.models.location import Stop, Location
from app.services.route_optimizer import RouteOptimizerService

# 차량 정보
vehicles = [
    Vehicle(
        id="v_001",
        name="Truck #1",
        vehicle_type="large",
        capacity=20000,
        fuel_consumption=8.5,
        fuel_cost_per_liter=1500,
        start_location_id="depot"
    )
]

# 배송 정류소
stops = [
    Stop(
        id="stop_001",
        name="Customer A",
        latitude=37.4979,
        longitude=127.0276,
        demand=5000
    ),
    Stop(
        id="stop_002",
        name="Customer B",
        latitude=35.1796,
        longitude=129.0756,
        demand=3000
    )
]

# 창고 위치
depot = Location(
    id="depot",
    name="Seoul Distribution Center",
    latitude=37.5665,
    longitude=126.9780
)

# 경로 최적화
optimizer = RouteOptimizerService()
result = optimizer.optimize(
    vehicles=vehicles,
    stops=stops,
    start_location=depot,
    time_limit_seconds=30
)

print(f"최적화 성공: {result.success}")
print(f"총 거리: {result.total_distance} km")
print(f"총 비용: {result.total_cost:,.0f} 원")
print(f"최적화 시간: {result.optimization_time_ms} ms")

for route in result.routes:
    print(f"\n차량 {route.vehicle_name}:")
    for stop in route.stops:
        print(f"  - {stop.stop_name}: {stop.cumulative_distance:.1f} km")
```

## 보안 고려사항

1. **API 키 관리**
   - `.env` 파일은 `.gitignore`에 추가
   - 프로덕션 환경에서는 환경 변수 사용
   - API 키 주기적 갱신

2. **Rate Limiting**
   - Google Cloud Console에서 할당량 설정
   - 비정상적인 사용 탐지

3. **데이터 보호**
   - 캐시된 데이터는 메모리에만 저장
   - 중요한 경로 정보는 암호화

## 참고자료

- [Google Maps API 문서](https://developers.google.com/maps/documentation)
- [Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix)
- [Google Cloud 콘솔](https://console.cloud.google.com)
- [API 할당량 및 요금](https://developers.google.com/maps/billing-and-pricing)
