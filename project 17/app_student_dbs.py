import streamlit as st
import sqlite3
import pandas as pd
from gemini_bot import text_to_sql_bot

# ---------------------------------------------------------
# Database Setup
# ---------------------------------------------------------
def init_db():
    """Initializes the SQLite database and creates the students table if it doesn't exist."""
    try:
        conn = sqlite3.connect("university.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                roll_no INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                course TEXT NOT NULL,
                marks REAL NOT NULL,
                grade TEXT NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

init_db()

# ---------------------------------------------------------
# UI Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Student Academic Records", page_icon="🎓")
st.title("Student Academic Records & Report Studio")

# Create tabs (Added Tab 3 for AI Assistant)
tab1, tab2, tab3 = st.tabs(["🎓 Register Student", "📊 Academic Reports", "🤖 AI Assistant"])

# ---------------------------------------------------------
# Tab 1: Register Student
# ---------------------------------------------------------
with tab1:
    st.header("Enroll a New Student")
    
    with st.form("register_form", clear_on_submit=True):
        roll_no = st.number_input("Roll Number", min_value=1, step=1)
        name = st.text_input("Full Name")
        department = st.selectbox("Department", ["Computer Science", "Data Science", "Electronics", "Mechanical"])
        course = st.text_input("Course Name")
        marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=0.1)
        
        submit_btn = st.form_submit_button("Register Student")
        
        if submit_btn:
            if not name.strip() or not course.strip():
                st.warning("Please fill out all text fields (Name and Course).")
            else:
                # Calculate grade
                if marks >= 90:
                    grade = 'A'
                elif marks >= 75:
                    grade = 'B'
                elif marks >= 60:
                    grade = 'C'
                else:
                    grade = 'D'
                
                # Insert into DB
                try:
                    conn = sqlite3.connect("university.db")
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO students (roll_no, name, department, course, marks, grade)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (roll_no, name, department, course, marks, grade))
                    conn.commit()
                    st.success(f"Success! Registered {name} (Roll No: {roll_no}) with Grade '{grade}'.")
                except sqlite3.IntegrityError:
                    st.error(f"Failed: A student with Roll Number {roll_no} already exists.")
                except sqlite3.Error as e:
                    st.error(f"Database error: {e}")
                finally:
                    if 'conn' in locals():
                        conn.close()

# ---------------------------------------------------------
# Tab 2: Academic Reports
# ---------------------------------------------------------
with tab2:
    st.header("Database Query & Visualization")
    
    report_options = {
        "All Students List": ("SELECT * FROM students;", "name"),
        "Top Performers (>= 75 Marks)": ("SELECT name, department, marks, grade FROM students WHERE marks >= 75 ORDER BY marks DESC;", "name"),
        "Department-wise Average Marks": ("SELECT department, AVG(marks) AS avg_marks FROM students GROUP BY department;", "department"),
        "Grade Breakdown Count": ("SELECT grade, COUNT(*) AS total_students FROM students GROUP BY grade;", "grade"),
        "Custom SQL Query": ("", None)
    }
    
    selection = st.selectbox("Select Report Operation", list(report_options.keys()))
    
    if selection == "Custom SQL Query":
        sql_query = st.text_area("Write your SQL statement here:", "SELECT * FROM students;")
        chart_index = None
    else:
        sql_query, chart_index = report_options[selection]
    
    st.markdown("**Executed SQL Query:**")
    st.code(sql_query, language="sql")
    
    if sql_query.strip():
        try:
            conn = sqlite3.connect("university.db")
            df = pd.read_sql_query(sql_query, conn)
            
            st.markdown("**Dataset Result:**")
            st.dataframe(df, use_container_width=True)
            
            generate_chart = st.checkbox("Generate Chart Visualization")
            
            if generate_chart:
                if df.empty:
                    st.info("The dataset is empty. Nothing to visualize.")
                else:
                    numeric_cols = df.select_dtypes(include='number').columns.tolist()
                    if not numeric_cols:
                        st.warning("No numerical data available in this dataset to generate a bar chart.")
                    else:
                        if "roll_no" in numeric_cols and len(numeric_cols) > 1:
                            numeric_cols.remove("roll_no")
                            
                        if chart_index and chart_index in df.columns:
                            chart_df = df.set_index(chart_index)[numeric_cols]
                        else:
                            text_cols = df.select_dtypes(exclude='number').columns.tolist()
                            if text_cols:
                                chart_df = df.set_index(text_cols[0])[numeric_cols]
                            else:
                                chart_df = df[numeric_cols]
                        
                        st.bar_chart(chart_df)
                        
        except sqlite3.Error as e:
            st.error(f"SQL Execution Error: {e}")
        except Exception as e:
            st.error(f"Application Error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

# ---------------------------------------------------------
# Tab 3: AI Assistant (Natural Language to SQL via Gemini)
# ---------------------------------------------------------
with tab3:
    st.header("🤖 AI Natural Language to SQL Assistant")
    st.markdown("Type what records or metrics you want to see in plain English. Gemini will apply database schema rules, generate the SQL query, and execute it.")
    
    user_prompt = st.text_input("Ask a question about student data:", placeholder="e.g., Show me all students in Computer Science with marks greater than 80")
    
    if st.button("Generate & Run Query"):
        if not user_prompt.strip():
            st.warning("Please type a valid request.")
        else:
            with st.spinner("Gemini is analyzing schema rules and crafting the SQL..."):
                sql_result, explanation_result = text_to_sql_bot(user_prompt)
            
            st.subheader("Generated Rules & Explanation")
            st.info(explanation_result)
            
            st.subheader("Generated SQL Query")
            st.code(sql_result, language="sql")
            
            # Automatically execute the generated query
            if sql_result.strip():
                try:
                    conn = sqlite3.connect("university.db")
                    df_ai = pd.read_sql_query(sql_result, conn)
                    
                    st.subheader("Query Results")
                    st.dataframe(df_ai, use_container_width=True)
                    
                except sqlite3.Error as e:
                    st.error(f"SQL Execution Error from AI Generated Code: {e}")
                finally:
                    if 'conn' in locals():
                        conn.close()