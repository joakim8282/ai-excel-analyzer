import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("📊 Excel 자동 분석기")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.subheader("📌 데이터 미리보기")
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    if numeric_cols:

        stats_summary = df[numeric_cols].describe().to_string()

        # ✅ 추가 (이거 빠졌었음)
        sample_data = df.head(20).to_string()

        st.subheader("📊 기본 통계")
        st.text(stats_summary)

        if st.button("AI 인사이트 생성"):

            prompt = f"""
너는 데이터 분석 전문가다.

아래는 데이터 일부와 통계 요약이다.

[샘플 데이터]
{sample_data}

[통계 요약]
{stats_summary}

이 데이터를 분석해서:
1. 주요 특징
2. 이상치 가능성
3. 눈에 띄는 패턴
을 설명해라.
"""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            insight = response.choices[0].message.content

            st.subheader("🧠 AI 분석 리포트")
            st.write(insight)

        st.subheader("📈 데이터 시각화")
        
        st.subheader("🚨 이상치 탐지")

        import numpy as np

        outlier_col = st.selectbox("이상치 확인할 컬럼 선택", numeric_cols, key="outlier_col")

        Q1 = df[outlier_col].quantile(0.25)
        Q3 = df[outlier_col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[outlier_col] < lower_bound) | (df[outlier_col] > upper_bound)]

        st.write(f"이상치 개수: {len(outliers)}")

        if len(outliers) > 0:
            st.dataframe(outliers)

            fig, ax = plt.subplots()
            ax.boxplot(df[outlier_col])
            ax.set_title(f"{outlier_col} 이상치 시각화")

            st.pyplot(fig)

        st.subheader("🔗 상관관계 분석")

        corr = df[numeric_cols].corr()

        st.dataframe(corr)

        fig, ax = plt.subplots()
        cax = ax.matshow(corr)
        plt.colorbar(cax)

        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))

        ax.set_xticklabels(numeric_cols, rotation=90)
        ax.set_yticklabels(numeric_cols)

        st.pyplot(fig)

        st.subheader("📉 회귀 분석")

        import seaborn as sns

        x_col = st.selectbox("X축 선택", numeric_cols, key="x")
        y_col = st.selectbox("Y축 선택", numeric_cols, key="y")

        fig, ax = plt.subplots()
        sns.regplot(x=df[x_col], y=df[y_col], ax=ax)

        ax.set_title(f"{x_col} vs {y_col} 회귀 분석")

        st.pyplot(fig)


        st.subheader("📉 회귀 분석")

        import seaborn as sns

        x_col = st.selectbox("X축 선택", numeric_cols, key="x")
        y_col = st.selectbox("Y축 선택", numeric_cols, key="y")

        fig, ax = plt.subplots()
        sns.regplot(x=df[x_col], y=df[y_col], ax=ax)

        ax.set_title(f"{x_col} vs {y_col} 회귀 분석")

        st.pyplot(fig)


        
        chart_type = st.selectbox("그래프 타입 선택", ["line", "bar", "hist"])

        fig, ax = plt.subplots()

        if chart_type == "line":
            df[col].plot(kind='line', ax=ax)
        elif chart_type == "bar":
            df[col].plot(kind='bar', ax=ax)
        elif chart_type == "hist":
            df[col].plot(kind='hist', ax=ax)

        ax.set_title(f"{col} ({chart_type})")

        st.pyplot(fig)




        st.subheader("💬 데이터에 대해 질문하기")

        user_question = st.text_input("데이터에 대해 궁금한 점을 입력하세요")

        if st.button("질문하기", key="ask_btn"):

            if user_question:

                sample_data = df.head().to_string()

                prompt = f"""
너는 데이터 분석 전문가다.

[데이터 샘플]
{sample_data}

[통계 요약]
{stats_summary}

[사용자 질문]
{user_question}

데이터 기반으로 설명해라.
"""

                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                answer = response.choices[0].message.content

                st.subheader("🤖 AI 답변")
                st.write(answer)

            else:
                st.warning("질문을 입력해주세요.")

        else:
            st.warning("숫자형 컬럼이 없습니다.")
