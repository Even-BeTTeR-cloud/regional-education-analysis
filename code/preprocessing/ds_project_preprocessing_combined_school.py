"""
학교 데이터 전처리 스크립트
School Data Preprocessing Script
"""

import pandas as pd
import sys


def main():
    """메인 함수"""
    
    # 파일 경로 설정
    input_file = 'raw_data/combined_school.xlsx'
    output_csv = 'processed_data/preprocessed_combined_school.csv'
    
    try:
        # 1. 데이터 로드
        df = pd.read_excel(input_file)
        
        # 2. 필요한 컬럼만 선택
        keep_columns = ['시도', '지역규모', '학교급', '학교명', '통합구분', '학급수', '학생수']
        df = df[keep_columns].copy()
        
        # 3. 컬럼명 영문 변환
        column_mapping = {
            '시도': 'province',
            '지역규모': 'region_size',
            '학교급': 'school_level',
            '학교명': 'school_name',
            '통합구분': 'integration_type',
            '학급수': 'class_count',
            '학생수': 'student_count'
        }
        df.rename(columns=column_mapping, inplace=True)
        
        # 4. 데이터 타입 변환
        dtype_mapping = {
            'province': 'category',
            'region_size': 'category',
            'school_level': 'category',
            'school_name': 'string',
            'integration_type': 'category',
            'class_count': 'int16',
            'student_count': 'int16'
        }
        
        for col, dtype in dtype_mapping.items():
            df[col] = df[col].astype(dtype)
        
        # 5. 데이터 저장
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        
        print("전처리 완료")
        print(f"출력 파일: {output_csv}")
        
        return 0
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
