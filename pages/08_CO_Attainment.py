
"""
pages/08_CO_Attainment.py
Simple CO Attainment
"""

import streamlit as st
import pandas as pd
from database.connection import get_connection
from database.co_distribution import get_courses

st.title("📈 CO Attainment")
st.caption("Simple Direct CO Attainment")

courses=get_courses()
if not courses:
    st.warning("No courses available.")
    st.stop()

course_map={f"{r[0]} - {r[1]}":r[0] for r in courses}
course_label=st.selectbox("Course", list(course_map.keys()))
course_code=course_map[course_label]

def calculate(course_code):
    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
        SELECT co_no,SUM(allocated_marks)
        FROM co_distribution
        WHERE course_code=?
        GROUP BY co_no
        ORDER BY co_no
    """, (course_code,))
    cos=cur.fetchall()

    cur.execute("""
        SELECT reg_no,le,s1,s2
        FROM student_marks
        WHERE course_code=?
    """, (course_code,))
    students=cur.fetchall()

    total_students=len(students)
    results=[]

    cur.execute("DELETE FROM direct_attainment WHERE course_code=?", (course_code,))

    for row in cos:
        co=row["co_no"] if hasattr(row,"keys") else row[0]
        max_marks=float((row["SUM(allocated_marks)"] if hasattr(row,"keys") else row[1]) or 0)
        target=0.6*max_marks
        qualified=0
        total=0

        for s in students:
            score=float((s["le"] or 0)+(s["s1"] or 0)+(s["s2"] or 0))
            total+=score
            if score>=target:
                qualified+=1

        percent=(qualified/total_students*100) if total_students else 0

        if percent>=70:
            level=3
        elif percent>=60:
            level=2
        else:
            level=1

        cur.execute(
            "INSERT OR REPLACE INTO direct_attainment(course_code,co_no,attainment) VALUES(?,?,?)",
            (course_code,co,level)
        )

        results.append({
            "CO":co,
            "Max Marks":round(max_marks,2),
            "Target":round(target,2),
            "Qualified":qualified,
            "Attainment %":round(percent,2),
            "Level":level
        })

    conn.commit()
    conn.close()
    return pd.DataFrame(results)

if st.button("📊 Calculate CO Attainment", use_container_width=True):
    df=calculate(course_code)
    if df.empty:
        st.warning("No CO Distribution found.")
    else:
        st.success("CO Attainment calculated.")
        st.dataframe(df, use_container_width=True, hide_index=True)
        c1,c2,c3=st.columns(3)
        c1.metric("COs", len(df))
        c2.metric("Average Level", round(df["Level"].mean(),2))
        c3.metric("Average %", round(df["Attainment %"].mean(),2))
