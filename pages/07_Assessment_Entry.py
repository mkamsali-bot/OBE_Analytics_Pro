"""
pages/07_Student_Marks.py
Simple Student Marks Entry
"""
import streamlit as st
import pandas as pd

from database.co_distribution import get_courses
from database.student_marks import (
    get_students_by_course,
    save_bulk_marks,
    clear_course_marks,
)

st.title("📝 Student Marks")
st.caption("Enter LE, S1 and S2 marks")

courses=get_courses()
if not courses:
    st.warning("No courses available.")
    st.stop()

course_map={f"{r[0]} - {r[1]}":r[0] for r in courses}
course_label=st.selectbox("Course",list(course_map.keys()))
course_code=course_map[course_label]

rows=get_students_by_course(course_code)

if rows:
    df=pd.DataFrame(rows,columns=["Reg No","Student Name","LE","S1","S2"])
else:
    df=pd.DataFrame(columns=["Reg No","Student Name","LE","S1","S2"])

edited=st.data_editor(
    df,
    hide_index=True,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "LE":st.column_config.NumberColumn("LE",min_value=0),
        "S1":st.column_config.NumberColumn("S1",min_value=0),
        "S2":st.column_config.NumberColumn("S2",min_value=0),
    }
)

c1,c2=st.columns(2)

with c1:
    if st.button("💾 Save",use_container_width=True):
        students=[]
        for _,r in edited.iterrows():
            if pd.notna(r["Reg No"]) and pd.notna(r["Student Name"]):
                students.append({
                    "reg_no":str(r["Reg No"]),
                    "student_name":str(r["Student Name"]),
                    "le":int(r["LE"]) if pd.notna(r["LE"]) else 0,
                    "s1":int(r["S1"]) if pd.notna(r["S1"]) else 0,
                    "s2":int(r["S2"]) if pd.notna(r["S2"]) else 0,
                })
        save_bulk_marks(course_code,students)
        st.success("Student marks saved successfully.")
        st.rerun()

with c2:
    if st.button("🗑 Clear Course Marks",use_container_width=True):
        clear_course_marks(course_code)
        st.success("Course marks deleted.")
        st.rerun()

st.divider()
st.subheader("Summary")
st.metric("Students",len(edited))
if not edited.empty:
    st.metric("Average LE",round(edited["LE"].fillna(0).mean(),2))
    st.metric("Average S1",round(edited["S1"].fillna(0).mean(),2))
    st.metric("Average S2",round(edited["S2"].fillna(0).mean(),2))
