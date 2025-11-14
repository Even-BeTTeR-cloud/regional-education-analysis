import pandas as pd
import re

# Step 1: 파일 로드 및 1행 제거
# skiprows=[0]으로 Column1~Column41 행 제거
# header=[0, 1]로 2행과 3행을 멀티인덱스 헤더로 설정
df = pd.read_csv('raw_data/regional_GDP.csv', 
                 encoding='cp949', 
                 skiprows=[0], 
                 header=[0, 1])

# Step 2: 멀티인덱스 컬럼을 단일 컬럼으로 재구성
# 첫 번째 컬럼('시도별')은 그대로 유지
# 나머지 컬럼은 '연도_지표명' 형태로 결합
new_columns = []
for col in df.columns:
    if col[0] == '시도별':
        # 첫 번째 컬럼은 '시도별'로 유지
        new_columns.append('시도별')
    else:
        # 연도에서 숫자만 추출 (예: '2023 p)' -> '2023')
        year = re.sub(r'[^0-9]', '', str(col[0]))
        # 연도_지표명 형태로 결합
        new_columns.append(f"{year}_{col[1]}")

df.columns = new_columns

# Step 3: "전국" 행 삭제
df = df[df['시도별'] != '전국']

# Step 4: Melting 수행 (Wide -> Long 형태 변환)
# id_vars: 고정할 컬럼 (지역명)
# var_name: 녹인 컬럼명이 들어갈 새 컬럼명
# value_name: 값이 들어갈 새 컬럼명
df_melted = df.melt(
    id_vars=['시도별'],
    var_name='year_indicator',
    value_name='value'
)


# year_indicator 컬럼을 '_'로 분리하여 year와 indicator 컬럼 생성
# n=1: 첫 번째 '_'에서만 분리 (지표명에 '_'가 있을 수 있으므로)
df_melted[['year', 'indicator']] = df_melted['year_indicator'].str.split('_', n=1, expand=True)

# 더 이상 필요 없는 year_indicator 컬럼 삭제
df_melted = df_melted.drop('year_indicator', axis=1)

# Step 5: Pivoting으로 Wide 형태로 변환 (Long -> Wide)
# index: 행 인덱스로 사용할 컬럼들 (시도별, year)
# columns: 열로 펼칠 컬럼 (indicator)
# values: 각 셀에 들어갈 값
df_final = df_melted.pivot_table(
    index=['시도별', 'year'],
    columns='indicator',
    values='value',
    aggfunc='first'  # 중복값이 있을 경우 첫 번째 값 사용
)

# 인덱스를 일반 컬럼으로 변환
df_final = df_final.reset_index()

# pivot_table 결과의 컬럼명이 다중 인덱스인 경우를 대비해 flatten
df_final.columns.name = None

# Step 6: 컬럼명 영어로 변경
column_mapping = {
    '시도별': 'region',
    '1인당 지역내총생산': 'gdp_per_capita',
    '1인당 지역총소득': 'gni_per_capita',
    '1인당 개인소득': 'personal_income_per_capita',
    '1인당 민간소비': 'private_consumption_per_capita'
}

df_final = df_final.rename(columns=column_mapping)

# 데이터 타입 변환
# year를 정수형으로 변환
df_final['year'] = df_final['year'].astype(int)

# 값 컬럼들을 숫자형으로 변환 (결측치가 있을 수 있으므로 errors='coerce' 사용)
value_columns = ['gdp_per_capita', 'gni_per_capita', 
                 'personal_income_per_capita', 'private_consumption_per_capita']

for col in value_columns:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

# 결측치 확인
print("\n결측치 확인:")
print(df_final.isnull().sum())

# 데이터 타입 확인
print("\n데이터 타입:")
print(df_final.dtypes)

# 최종 결과 미리보기
print("\n최종 전처리 결과:")
print(df_final.head(20))
print(f"\n최종 데이터 shape: {df_final.shape}")

# 기본 통계 정보
print("\n기본 통계 정보:")
print(df_final.describe())

# 결과를 CSV 파일로 저장
output_path = 'processed_data/preprocessed_regional_gdp.csv'
df_final.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n전처리된 데이터가 '{output_path}'에 저장되었습니다.")
