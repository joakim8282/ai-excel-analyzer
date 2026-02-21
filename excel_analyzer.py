import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("📊 Excel 자동 분석기")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # -------------------------------
    # 📌 데이터 미리보기
    # -------------------------------
    st.subheader("📌 데이터 미리보기")
    st.dataframe(df.head())

    # -------------------------------
    # 🔍 데이터 필터
    # -------------------------------
    st.subheader("🔍 데이터 필터")

    filter_col = st.selectbox("필터 컬럼 선택", df.columns)
    unique_vals = df[filter_col].dropna().unique()
    selected_val = st.selectbox("값 선택", unique_vals)

    filtered_df = df[df[filter_col] == selected_val]

    st.write("필터 적용 데이터")
    st.dataframe(filtered_df.head())

    # 👉 핵심: 분석용 데이터
    analysis_df = filtered_df if len(filtered_df) > 0 else df

    # -------------------------------
    # 📊 숫자 컬럼 추출
    # -------------------------------
    numeric_cols = analysis_df.select_dtypes(include=['number']).columns.tolist()

    if numeric_cols:

        # -------------------------------
        # 📊 기본 통계
        # -------------------------------
        stats_summary = analysis_df[numeric_cols].describe().to_string()
        sample_data = analysis_df.head(20).to_string()

        st.subheader("📊 기본 통계")
        st.text(stats_summary)

        # -------------------------------
        # 🧠 AI 분석
        # -------------------------------
        if st.button("AI 인사이트 생성"):

            prompt = f"""
너는 데이터 분석 전문가다.

[샘플 데이터]
{sample_data}

[통계 요약]
{stats_summary}

이 데이터를 분석해서:
1. 주요 특징
2. 이상치 가능성
3. 패턴
을 설명해라.
"""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            insight = response.choices[0].message.content

            st.subheader("🧠 AI 분석 리포트")
            st.write(insight)

        # -------------------------------
        # 🚨 이상치 탐지
        # -------------------------------
        st.subheader("🚨 이상치 탐지")

        outlier_col = st.selectbox("이상치 컬럼", numeric_cols)

        Q1 = analysis_df[outlier_col].quantile(0.25)
        Q3 = analysis_df[outlier_col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = analysis_df[
            (analysis_df[outlier_col] < lower_bound) |
            (analysis_df[outlier_col] > upper_bound)
        ]

        st.write(f"이상치 개수: {len(outliers)}")

        if len(outliers) > 0:
            st.dataframe(outliers)

            fig, ax = plt.subplots()
            ax.boxplot(analysis_df[outlier_col])
            ax.set_title(f"{outlier_col} Boxplot")
            st.pyplot(fig)

        # -------------------------------
        # 🔗 상관관계
        # -------------------------------
        st.subheader("🔗 상관관계 분석")

        corr = analysis_df[numeric_cols].corr()
        st.dataframe(corr)

        fig, ax = plt.subplots()
        cax = ax.matshow(corr)
        plt.colorbar(cax)

        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=90)
        ax.set_yticklabels(numeric_cols)

        st.pyplot(fig)

        # -------------------------------
        # 📉 회귀 분석
        # -------------------------------
        st.subheader("📉 회귀 분석")

        x_col = st.selectbox("X 선택", numeric_cols, key="x")
        y_col = st.selectbox("Y 선택", numeric_cols, key="y")

        fig, ax = plt.subplots()
        sns.regplot(x=analysis_df[x_col], y=analysis_df[y_col], ax=ax)

        ax.set_title(f"{x_col} vs {y_col}")
        st.pyplot(fig)

        # -------------------------------
        # 📈 그래프
        # -------------------------------
        st.subheader("📈 데이터 시각화")

        col = st.selectbox("컬럼 선택", numeric_cols)
        chart_type = st.selectbox("그래프 타입", ["line", "bar", "hist"])

        fig, ax = plt.subplots()

        if chart_type == "line":
            analysis_df[col].plot(kind='line', ax=ax)
        elif chart_type == "bar":
            analysis_df[col].plot(kind='bar', ax=ax)
        elif chart_type == "hist":
            analysis_df[col].plot(kind='hist', ax=ax)

        ax.set_title(f"{col} ({chart_type})")
        st.pyplot(fig)

    else:
        st.warning("숫자형 컬럼이 없습니다.")

    # -------------------------------
    # 💬 질문 기능 (항상 사용 가능)
    # -------------------------------
    st.subheader("💬 데이터에 대해 질문하기")

    user_question = st.text_input("질문 입력")

    if st.button("질문하기"):

        if user_question:

            sample_data = analysis_df.head().to_string()

            prompt = f"""
너는 데이터 분석 전문가다.

[데이터]
{sample_data}

[통계]
{stats_summary if numeric_cols else "없음"}

[질문]
{user_question}

데이터 기반으로 답변해라.
"""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            answer = response.choices[0].message.content

            st.subheader("🤖 AI 답변")
            st.write(answer)

        else:
            st.warning("질문을 입력하세요.")
