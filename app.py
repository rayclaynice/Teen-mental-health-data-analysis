import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go




#custom page loading spinner icon
spinner_html = """
<style>
.brain-spinner {
    font-size: 140px;
    animation: rotateBrain 2.2s linear infinite;
    display: block;
    margin: 0 auto;
    filter: drop-shadow(0 0 25px #00D4AA);
}
@keyframes rotateBrain {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
</style>
<div style="text-align: center; padding: 60px 0;">
    <div class="brain-spinner">🧠</div>
    <p style="font-size: 20px; margin-top: 20px; color: #00D4AA; font-weight: 500;">
        Loading dashboard...<br>Analyzing social media impact on teen well-being 🧠 🧬
    </p>
</div>
"""



#page configuration
st.set_page_config(page_title="Teen Mental Health", page_icon="🧠", layout="wide")

spinner_placeholder = st.empty()

with spinner_placeholder:
    st.iframe(spinner_html, height=320)

@st.cache_data













                                                                    #functions


#function to load dataset/clean dataset and create bins
def load_data():
    df = pd.read_csv("teen_social_media_mental_health.csv")
    df.columns = df.columns.str.lower().str.strip()
    df["usage_level"] = pd.cut(
        df["daily_social_media_hours"],
        bins=[0, 2, 4, 6, 24],
        labels=["0-2 hrs", "2-4 hrs", "4-6 hrs", "6+ hrs"]
    )
    df["sleep_group"] = pd.cut(
        df["sleep_hours"],
        bins=[0, 4, 5, 6, 7, 10],
        labels=["0–4 hrs", "4–5 hrs", "5–6 hrs", "6–7 hrs", "7+ hrs"]
    )
    return df

df = load_data()


# Functions to find correlation between differentcolumns 
def correlations(df):
    return (
        round(df["daily_social_media_hours"].corr(df["sleep_hours"]), 2),
        round(df["daily_social_media_hours"].corr(df["stress_level"]), 2),
        round(df["sleep_hours"].corr(df["anxiety_level"]), 2),
        round(df["addiction_level"].corr(df["academic_performance"]), 2),
        round(df["physical_activity"].corr(df["anxiety_level"]), 2)
    )


#function to find totals
def summary_counts(df):
    gender_counts = df["gender"].value_counts()
    return {
        "total_male": gender_counts.get("male", 0),
        "total_female": gender_counts.get("female", 0),
    }


#function to find average
def avg_sleep_hours(df):
    return round(df["sleep_hours"].mean(), 1), round(df["stress_level"].mean(), 1)

#function to find averages
def avg_usage_per_platform(df):
    avg_tiktok = round(df[df["platform_usage"] == "TikTok"]["daily_social_media_hours"].mean(), 1)
    avg_instagram = round(df[df["platform_usage"] == "Instagram"]["daily_social_media_hours"].mean(), 1)
    avg_academic = round(df["academic_performance"].mean(), 1)
    return avg_tiktok, avg_instagram, avg_academic

#function to find average media hr per male/female gender
def avg_media_hr_by_gender(df):
    avg_hr_male = round(df[df["gender"] == "male"]["daily_social_media_hours"].mean(), 1)
    avg_hr_female = round(df[df["gender"] == "female"]["daily_social_media_hours"].mean(), 1)
    return avg_hr_male, avg_hr_female


#Average media hr by age 
def avg_media_hr_age(df):
    return round(df.groupby("age")["daily_social_media_hours"].mean(), 1)

#Average media hr per male/female gender
def platform_usage_by_age(df):
    return df.groupby(["age", "platform_usage"]).size().reset_index(name="count")

#Average paltform usage by gender
def platform_usage_by_gender_count(df):
    return df.groupby(["gender", "platform_usage"]).size().reset_index(name="count")

#Averegae media time by gender
def media_time_gender(df):
    summary = df.groupby(["usage_level", "gender"]).size().reset_index(name="count")
    summary["percentage"] = summary.groupby("gender")["count"].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    return summary

#usage vs depression
def usage_vs_depression(df):
    return df.groupby(["usage_level", "depression_label"]).size().reset_index(name="count")

#depression across gender
def depression_across_gender(df):
    return df.groupby(["usage_level", "depression_label", "gender"]).size().reset_index(name="count")

#risk score calculation
def calculate_risk_score(df):
    df = df.copy()
    df["stress_norm"]    = (df["stress_level"] / df["stress_level"].max()) * 10
    df["anxiety_norm"]   = (df["anxiety_level"] / df["anxiety_level"].max()) * 10
    df["addiction_norm"] = (df["addiction_level"] / df["addiction_level"].max()) * 10
    df["sleep_norm"]     = (df["sleep_hours"] / df["sleep_hours"].max()) * 10
    df["activity_norm"]  = (df["physical_activity"] / df["physical_activity"].max()) * 10
    df["risk_score"] = (
        (df["stress_norm"] * 25) +
        (df["anxiety_norm"] * 25) +
        (df["addiction_norm"] * 25) -
        (df["sleep_norm"] * 15) -
        (df["activity_norm"] * 10)
    )
    df["risk_score"] = (
        (df["risk_score"] - df["risk_score"].min()) /
        (df["risk_score"].max() - df["risk_score"].min()) * 100
    ).round(1)
    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[0, 25, 50, 75, 100],
        labels=["Low", "Moderate", "High", "Very High"]
    )
    return df




                                                                        #FUNCTION
#platform usage per gender (pie chart)
def platform_pie(df, gender):
    filtered = df[df["gender"] == gender]["platform_usage"].value_counts().reset_index()
    filtered.columns = ["platform", "count"]
    fig = px.pie(
        filtered,
        values="count",
        names="platform",
        title=f"{gender.capitalize()} Platform Usage Breakdown",
        hole=0.3, template="plotly_dark"
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

#all number card design
def metric_card(label, value):
    st.markdown(f"""
        <div style="background-color:#2C2F3F; border-radius:12px; padding:1.25rem;
                    text-align:center; border:0.5px solid #3d4155;">
            <div style="font-size:48px; font-weight:500; color:#00D4AA;">{value}</div>
            <div style="font-size:15px; color:#00D4AA; margin-top:8px;">{label}</div>
        </div>
    """, unsafe_allow_html=True)


#streamlit figure container design 
def chart_card(fig):
    with st.container():
        st.markdown("""
            <style>
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"]:has(div.chart-wrapper) {
                background-color: #1E2130;
                border: 1px solid #5A6080;
                border-radius: 12px;
                padding: 1rem;
            }
            </style>
            <div class="chart-wrapper"></div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig, width="stretch")


#Header Section
def section_header(title):
    st.markdown(f"""
        <h2 style="font-size:22px; font-weight:500; color:#00D4AA;
                   margin-bottom:0.5rem; margin-top:1rem;">
            {title}
        </h2>
    """, unsafe_allow_html=True)

#insight box 
def insight_box(key, default_text):
    st.text_area(
        "Insight", value=default_text, height=100,
        key=key, label_visibility="collapsed"
    )











                                                                    # Calling all Functions

media_vs_sleep, media_vs_stress, sleep_vs_anxiety, addiction_vs_academic, activities_vs_anxiety = correlations(df)
metrics = summary_counts(df)
avg_sleep, avg_stress = avg_sleep_hours(df)
avg_tiktok, avg_instagram, avg_academic = avg_usage_per_platform(df)
avg_hr_male, avg_hr_female = avg_media_hr_by_gender(df)
avg_hr_age = avg_media_hr_age(df).reset_index()
plat_by_age = platform_usage_by_age(df)
plat_by_gender = platform_usage_by_gender_count(df)
gender_media = media_time_gender(df)
depression_by_usage = usage_vs_depression(df)
animated_df = depression_across_gender(df)
sleep_academic = df.groupby("sleep_group")["academic_performance"].mean().reset_index().round(2)
df = calculate_risk_score(df)

avg_risk = round(df["risk_score"].mean(), 1)
high_risk = len(df[df["risk_level"].isin(["High", "Very High"])])
high_risk_pct = round(high_risk / len(df) * 100, 1)
very_high_count = len(df[df["risk_level"] == "Very High"])
risk_by_gender = df.groupby(["gender", "risk_level"]).size().reset_index(name="count")
risk_by_age = df.groupby(["age", "risk_level"]).size().reset_index(name="count")
heatmap_data = df.groupby(["age", "gender"])["risk_score"].mean().round(1).reset_index()
heatmap_pivot = heatmap_data.pivot(index="age", columns="gender", values="risk_score")







                                                                #STREAMLIT BODY 
TEMPLATE = "plotly_dark"
TRANSPARENT = {"paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)"}


corr_df = pd.DataFrame({
    "relationship": ["Social Media vs Sleep", "Social Media vs Stress",
                        "Sleep vs Anxiety", "Addiction vs Academic", "Physical Activity vs Anxiety"],
    "correlation": [media_vs_sleep, media_vs_stress, sleep_vs_anxiety,
                    addiction_vs_academic, activities_vs_anxiety]
}).sort_values("correlation")



#Social Media Habits & Mental Health Bar Chart
fig_corr = px.bar(corr_df, x="correlation", y="relationship", orientation="h",
    title="Correlation: Social Media Habits & Mental Health",
    labels={"correlation": "Correlation Score", "relationship": ""},
    color="correlation", color_continuous_scale="RdYlGn", template=TEMPLATE)
fig_corr.add_vline(x=0, line_dash="dash", line_color="gray")
fig_corr.update_layout(showlegend=False, xaxis_range=[-1, 1], **TRANSPARENT)


#Social Media Hours by Gender Bar Chart
fig_gender_usage = px.bar(gender_media, x="usage_level", y="percentage", color="gender",
    barmode="group", title="Social Media Hours by Gender",
    labels={"usage_level": "Daily Social Media Hours", "percentage": "Percentage (%)", "gender": "Gender"},
    template=TEMPLATE)
fig_gender_usage.update_layout(**TRANSPARENT)

#Avg Academic Performance by Sleep Duration Bar Chart
fig_sleep_academic = px.bar(sleep_academic, x="sleep_group", y="academic_performance",
    color="sleep_group", title="Avg Academic Performance by Sleep Duration",
    labels={"sleep_group": "Sleep Hours", "academic_performance": "Academic Performance"},
    template=TEMPLATE)
fig_sleep_academic.update_layout(**TRANSPARENT)

#Social Media Hours vs Depression Bar Chart
fig_depression = px.bar(depression_by_usage, x="usage_level", y="count", color="depression_label",
    barmode="group", title="Social Media Hours vs Depression",
    labels={"usage_level": "Daily Social Media Hours", "count": "Number of Teenagers",
            "depression_label": "Depressed"},
    template=TEMPLATE)
fig_depression.add_vline(x=2, line_dash="dash", line_color="red",
    annotation_text="Risk Threshold", annotation_position="top right")
fig_depression.update_layout(**TRANSPARENT)

#Depression by Gender across Usage Levels Bar Chart
fig_animated = px.bar(animated_df, x="gender", y="count", color="depression_label",
    animation_frame="usage_level", barmode="group",
    title="Depression by Gender across Usage Levels",
    labels={"gender": "Gender", "count": "Number of Teenagers",
            "depression_label": "Depressed", "usage_level": "Usage Level"},
    template=TEMPLATE)
fig_animated.update_layout(**TRANSPARENT)


#Sleep Hours vs Anxiety by Gender Scatter Plot
fig_sleep_anxiety = px.scatter(df, x="sleep_hours", y="anxiety_level", color="gender",
    trendline="ols", facet_col="gender", title="Sleep Hours vs Anxiety by Gender",
    labels={"sleep_hours": "Sleep Hours", "anxiety_level": "Anxiety Level"},
    template=TEMPLATE)
fig_sleep_anxiety.update_layout(**TRANSPARENT)

#Sleep Hours vs Stress by Gender Scatter Plot
fig_sleep_stress = px.scatter(df, x="sleep_hours", y="stress_level", color="gender",
    trendline="ols", facet_col="gender", title="Sleep Hours vs Stress by Gender",
    labels={"sleep_hours": "Sleep Hours", "stress_level": "Stress Level"},
    template=TEMPLATE)
fig_sleep_stress.update_layout(**TRANSPARENT)

#Physical Activity vs Addiction Level Scatter Plot
fig_activity = px.scatter(df, x="physical_activity", y="addiction_level", color="gender",
    size="addiction_level", trendline="ols", title="Physical Activity vs Addiction Level",
    labels={"physical_activity": "Physical Activity", "addiction_level": "Addiction Level"},
    template=TEMPLATE)
fig_activity.update_layout(**TRANSPARENT)

#Social Media Hours Distribution by Gender_violin
fig_violin_usage = px.violin(df, x="gender", y="daily_social_media_hours", color="gender",
    box=True, points="all", title="Social Media Hours Distribution by Gender",
    labels={"gender": "Gender", "daily_social_media_hours": "Daily Social Media Hours"},
    template=TEMPLATE)
fig_violin_usage.update_layout(**TRANSPARENT)

#Addiction Level by Usage Level box
fig_box_addiction = px.box(df, x="usage_level", y="addiction_level", color="usage_level",
    title="Addiction Level by Usage Level",
    labels={"usage_level": "Daily Social Media Hours", "addiction_level": "Addiction Level"},
    template=TEMPLATE)
fig_box_addiction.update_layout(**TRANSPARENT)


#Stress Level by Usage Level and Gender Box
fig_box_stress = px.box(df, x="usage_level", y="stress_level", color="gender",
    facet_row="gender", title="Stress Level by Usage Level and Gender",
    labels={"usage_level": "Daily Social Media Hours", "stress_level": "Stress Level"},
    template=TEMPLATE)
fig_box_stress.update_layout(**TRANSPARENT)


#Average Mental Health Risk Score Risk Score
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number", value=avg_risk,
    title={"text": "Average Mental Health Risk Score"},
    gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#00D4AA"},
            "steps": [{"range": [0, 25], "color": "green"}, {"range": [25, 50], "color": "yellow"},
                        {"range": [50, 75], "color": "orange"}, {"range": [75, 100], "color": "red"}]}
))
fig_gauge.update_layout(template=TEMPLATE, **TRANSPARENT)

#Mental Health Risk Level by Gender Bar Chart
fig_risk_gender = px.bar(risk_by_gender, x="risk_level", y="count", color="gender",
    barmode="group", title="Mental Health Risk Level by Gender",
    labels={"risk_level": "Risk Level", "count": "Number of Teenagers"},
    category_orders={"risk_level": ["Low", "Moderate", "High", "Very High"]},
    template=TEMPLATE)
fig_risk_gender.update_layout(**TRANSPARENT)


#Mental Health Risk Level by Age Bar Chart
fig_risk_age = px.bar(risk_by_age, x="age", y="count", color="risk_level",
    barmode="stack", title="Mental Health Risk Level by Age",
    labels={"age": "Age", "count": "Number of Teenagers", "risk_level": "Risk Level"},
    category_orders={"risk_level": ["Low", "Moderate", "High", "Very High"]},
    color_discrete_map={"Low": "green", "Moderate": "yellow", "High": "orange", "Very High": "red"},
    template=TEMPLATE)
fig_risk_age.update_layout(**TRANSPARENT)


#Avg Risk Score by Age and Gender Heat map
fig_heatmap = px.imshow(heatmap_pivot, title="Avg Risk Score by Age and Gender",
    labels={"x": "Gender", "y": "Age", "color": "Risk Score"},
    color_continuous_scale="RdYlGn_r", text_auto=True, template=TEMPLATE)
fig_heatmap.update_layout(**TRANSPARENT)


#Risk Score Distribution by Gender Violin
fig_violin_risk = px.violin(df, x="gender", y="risk_score", color="gender",
    box=True, points="all", title="Risk Score Distribution by Gender",
    labels={"gender": "Gender", "risk_score": "Mental Health Risk Score"},
    template=TEMPLATE)
fig_violin_risk.update_layout(**TRANSPARENT)

fig_female = platform_pie(df, "female")
fig_male = platform_pie(df, "male")

spinner_placeholder.empty()





#Streamlit Layout
st.markdown("<h1 style='color:#00D4AA;'>Teen Social Media & Mental Health Dashboard</h1>",
            unsafe_allow_html=True)

#Overview Section 
section_header("Overview")
st.markdown("""
**This interactive dashboard provides a comprehensive analysis of the relationship between social media usage and mental health among teenagers.**

Based on a dataset of **5,000 teenagers**, the dashboard reveals several important insights:

- There are **2,436 males** and **2,564 females** in the study.
- Teens sleep an average of **6.1 hours** per night, notably below the recommended 8–10 hours for their age group.
- The average stress level stands at **5.3** (on a 10-point scale).
- Academic performance averages **2.4** (on a typical GPA scale).
- Teens spend an average of **4.5 hours** daily on social media, with nearly identical usage between males (**4.5 hrs**) and females (**4.5 hrs**).

The analysis explores how daily social media consumption, particularly on platforms like **TikTok** and **Instagram**, correlates with sleep quality, anxiety, depression risk, addiction levels, academic outcomes, and physical activity. 

It also features a composite **Mental Health Risk Score** to help identify teens at higher risk. Through interactive visualizations and statistical correlations, this dashboard aims to deliver clear, actionable insights into modern digital habits and their impact on teen well-being.
""")

st.write("")
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Total males", metrics["total_male"])
with col2:
    metric_card("Total females", metrics["total_female"])
with col3:
    metric_card("Avg sleep hours", avg_sleep)

st.write("")
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Avg stress level", avg_stress)
with col2:
    metric_card("Avg academic performance", avg_academic)
with col3:
    metric_card("Avg TikTok hours", avg_tiktok)

st.write("")
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Avg Instagram hours", avg_instagram)
with col2:
    metric_card("Avg male usage hours", avg_hr_male)
with col3:
    metric_card("Avg female usage hours", avg_hr_female)

st.divider()     #divides sections

# Section 2: Usage Patterns 
# === USAGE PATTERNS SECTION ===
section_header("Usage Patterns")

st.markdown("""
**Teenage social media usage varies significantly by gender, with clear platform preferences and concerning overall time spent online.**

This section analyzes daily social media habits across genders and platforms. The findings show that social media has become deeply embedded in teen daily routines:

- **Most teenagers (over 70%)** spend between **2 to 6 hours** per day on social media, with the **4–6 hour** range being the most common for both males and females.
- Usage distribution is broadly similar between genders, though males show slightly higher variability (some very light and some extremely heavy users).
- **Platform preferences are strongly gendered**:
  - **Males** show higher engagement with **TikTok** (≈30%).
  - **Females** show stronger preference for **Instagram** (≈30%).

The violin plots confirm that while average usage is comparable, the spread of behavior differs, males have more extreme cases, while female usage tends to cluster more tightly around the median.

These patterns matter because **different platforms deliver different content**. TikTok’s short-form, highly addictive videos and Instagram’s curated highlight-reel culture can influence self-esteem, sleep disruption, and stress in distinct ways.

### Recommendations:
- Encourage teens to set **daily social media time limits** (ideally under 4 hours) to reduce overall exposure.
- Promote **platform awareness**, help teens understand how different apps affect their mood and sleep.
- Parents can use built-in screen time tools or family media plans to foster healthier digital habits.
- Schools could run digital wellness workshops that address platform-specific risks (e.g., TikTok addiction vs Instagram comparison culture).
- Encourage replacing some social media time with offline activities, especially physical ones, to create better balance.
""")

col1, col2 = st.columns(2)
with col1:
    chart_card(fig_gender_usage)
with col2:
    chart_card(fig_violin_usage)

col1, col2 = st.columns(2)
with col1:
    chart_card(fig_male)
with col2:
    chart_card(fig_female)

st.divider()




                                                         
                                                                    #  CORRELATIONS SECTION 
section_header("Correlations")

st.markdown("""
**Social media usage shows strong negative correlations with sleep and positive correlations with stress, while physical activity appears protective.**

This section reveals several critical relationships in teen mental health:

- **Social Media vs Sleep** has the strongest negative correlation, the more time teens spend on social media, the less sleep they get. This is particularly concerning as adequate sleep is essential for adolescent brain development.
- **Social Media vs Stress** shows a strong **positive** correlation. Higher social media usage is associated with elevated stress levels.
- **Addiction Level vs Academic Performance** has a notable negative correlation, suggesting that addictive social media behaviors directly impact school results.
- **Sleep vs Anxiety** shows a negative relationship, teens who sleep more tend to experience lower anxiety.
- **Physical Activity vs Anxiety** has a weak protective effect, indicating that staying active can help buffer against anxiety.

The bar chart below further strengthens these findings: **Average Academic Performance improves significantly with more sleep**. Teens sleeping 7+ hours achieve substantially higher academic scores compared to those sleeping 0–4 hours. This creates a clear chain:

**Heavy Social Media Use → Less Sleep → Higher Stress & Anxiety → Lower Academic Performance**

These patterns highlight how digital habits can trigger a dangerous cascade effect on multiple aspects of teen well-being.

### Recommendations:
- **Limit social media use**, especially in the evening. Reducing screen time before bed can significantly improve sleep quality and break the negative cycle.
- **Promote physical activity** as a protective habit, even moderate daily exercise can help reduce anxiety and offset some negative effects of social media.
- **Educate teens on sleep hygiene** and the importance of 8+ hours of sleep. Schools and parents should consider implementing "no-phone" policies at night.
- **Monitor addiction signs** early. Teens showing high addiction levels need targeted support to prevent further decline in academic performance.
- Encourage **balanced routines**: combining reasonable social media limits with sufficient sleep and regular physical activity can substantially lower overall mental health risks.
""")

chart_card(fig_corr)

col1, col2 = st.columns(2)
with col1:
    chart_card(fig_sleep_anxiety)
with col2:
    chart_card(fig_sleep_stress)

col1, col2 = st.columns(2)
with col1:
    chart_card(fig_sleep_academic)
with col2:
    chart_card(fig_activity)

st.divider()

                                                            # Section 4: Depression & Addiction 
# DEPRESSION & ADDICTION SECTION 
section_header("Depression & Addiction")

st.markdown("""
**Higher social media usage is strongly associated with increased depression rates and addiction levels among teenagers.**

This section highlights the concerning relationship between daily screen time and mental health challenges:

- **Depression risk rises sharply with usage.** Teens using social media for **4–6 hours** per day show significantly higher depression counts compared to light users (0–2 hours). The risk remains elevated even at **6+ hours**.
- The stacked bar chart clearly shows that the **majority of depressed teens** fall into the moderate-to-high usage categories (2+ hours), with a visible jump after the 4-hour mark.
- Both **males and females** experience this trend, though the animated visualization reveals nuanced differences across usage levels.
- **Addiction levels** increase dramatically with usage. The box plot shows that teens in the 6+ hour group have the highest median addiction scores and greater variability, indicating stronger addictive behaviors.
- Stress levels also follow a similar pattern — higher usage correlates with elevated stress, particularly noticeable in the 4–6 hour and 6+ hour brackets.

These findings suggest a **dose-response relationship**: the more time teens spend on social media, the greater the likelihood of depressive symptoms, addictive patterns, and heightened stress. Excessive use appears to create a vicious cycle where addiction fuels more usage, further worsening mental health.

### Recommendations:
- Encourage teens to keep daily social media use **under 4 hours** when possible, as this appears to be a critical threshold.
- Promote **screen-free routines** before bedtime to protect sleep and reduce depression risk.
- Parents and educators should monitor for signs of addiction (especially in the 6+ hour group) and encourage balanced digital habits.
- Schools and mental health programs could consider targeted interventions for heavy users (4+ hours), including digital wellness education and promoting physical activity as a protective factor.
""")

chart_card(fig_depression)
chart_card(fig_animated)

col1, col2 = st.columns(2)
with col1:
    chart_card(fig_box_addiction)
with col2:
    chart_card(fig_box_stress)

st.divider()



                    
                                                            # MENTAL HEALTH RISK ANALYSIS SECTION 
section_header("Mental Health Risk Analysis")

st.markdown("""
**A composite Mental Health Risk Score was calculated using stress, anxiety, addiction, sleep, and physical activity levels. The results are concerning.**

### Key Findings:
- The **average risk score** across all teenagers is **44.6** (out of 100).
- **1,890 teenagers** (approximately **37.8%**) fall into the **High or Very High** risk category.
- Risk levels are remarkably similar between **males and females**, showing that excessive social media impact is not strongly gender-specific.
- Risk remains relatively consistent across ages **13 to 19**, with only slight increases in the oldest groups (18–19 years).

The gauge and heatmap visualizations confirm that no single age group or gender is dramatically safer, the risk is widespread. The violin plots show that while the average sits at a moderate level, there is a wide spread of scores, with many teens experiencing significantly higher risk (60–90+ range).

### What This Means:
This composite score reveals that over one-third of the studied teenagers are experiencing dangerous combinations of poor sleep, high stress, anxiety, and addictive social media behavior. The fact that risk is evenly distributed across genders and age groups suggests this is a **systemic issue** driven primarily by modern digital habits rather than individual demographics.

### Recommendations:
- **Early intervention is critical.** Schools and parents should prioritize digital wellness programs starting from age 13.
- Focus on **sleep improvement** and **physical activity** as the two most actionable protective factors that can lower the overall risk score.
- Targeted support should be provided to the **37.8%** of teens in the High/Very High risk group, including counseling, usage limits, and behavioral interventions.
- Encourage daily limits of **under 4 hours** of social media use, as higher usage strongly contributes to elevated risk scores.
- Regular mental health check-ins using tools like this risk score can help identify at-risk teens before symptoms become severe.
""")

#risk score cards
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Avg risk score", avg_risk)     #avg risk score from all rows
with col2:
    metric_card("High risk count", high_risk)    #total number of teenagers with high risk
with col3:
    metric_card("High risk %", f"{high_risk_pct}%")   #percentage that are at high risk

st.write("")

col1, col2 = st.columns(2)
with col1:
    chart_card(fig_gauge)     #avg mental health risk score
with col2:
    chart_card(fig_heatmap)   #avg risk score by age and gender

col1, col2 = st.columns(2)
with col1:
    chart_card(fig_risk_gender)  #mental health risk level by gender (low to very high)
with col2:
    chart_card(fig_risk_age)

chart_card(fig_violin_risk)     #risk score distribution by Gender

st.divider()

st.markdown("""
    <div style="text-align:center; color:#666; font-size:14px; margin-top:2rem;">
        Built with Streamlit · Teen Social Media & Mental Health · 2025
    </div>
""", unsafe_allow_html=True)