import streamlit as st  # to call the library
import os
from diet import bmi_calculator,bmr_calculator,tdee_calculator,calorie_target
from rag import load_rag
from openai import OpenAI
from dotenv import load_dotenv
##-------------------LLM----------------------------------##

load_dotenv()
HF_Token= os.getenv("HF_Token")

client= OpenAI(base_url="https://router.huggingface.co/v1",
               api_key=HF_Token)


##----------------LLM----------------------------------------##

st.set_page_config(layout="wide")

st.set_page_config(page_title="Health Assistance",
              page_icon="😊🍅",
              layout="wide")

st.title("AI Health Assistance 🍅")


st.write("Personal Helath Assitance and Diet Recommendation Agent")
st.header("Health Information")

st.sidebar.header("Your Information ℹ️")

# env\Scripts\python.exe -m streamlit run app.py (command to run it)

gender= st.sidebar.selectbox("Gender",["Male","Female"])
age= st.sidebar.number_input("Age",1,100)
weight= st.sidebar.number_input("Weight(kg)",1,120)
height= st.sidebar.number_input("Height(cm)",100,200)
activity= st.sidebar.selectbox("Activity",["Sedentary",             
                     "Lightly Active",
                     "Moderately Active",
                     "Very Active",
                     "Extra Active"])
aim= st.sidebar.selectbox("AIM",["weight maintain","weight loss","weight gain"])
diet_type= st.sidebar.selectbox("Diet Type",["Vegeterian","Non Vegeterian"])
allergies= st.sidebar.selectbox("Allergies",["Allergies","None"])

#------------------------------Control Area----------------------------------------------------------#

bmi=bmi_calculator(weight,height)
bmr=bmr_calculator(gender,age,weight,height)
tdee=tdee_calculator(bmr,activity)
calories=calorie_target(tdee,aim)

##-------------------------------------------------------##

col1,col2,col3,col4=st.columns(4)
col1.metric("BMI",bmi)
col2.metric("BMR",f"{bmr} kcal")
col3.metric("TDEE",f"{tdee} kcal")
col4.metric("Calorie Target",f"{calories} kcal")

tab1,tab2= st.tabs(["Diet Recommandation","Health Assitance"])
if tab1:
    if st.button("Recommend Diet"):
        if client:
            with st.spinner("Creating Diet..."):
                try:
                    db=load_rag()
                    search_query=f"""diet_type{diet_type}
                                       Healthy Food
                                       Protein
                                       Allergies"""
                    docs=db.similarity_search(search_query,3)
                    context="\n\n".join([ doc.page_content for doc in docs])
                    prompt=f"""You are a helpful AI nutrition assistant.



Use the following nutrition knowledge

to create a simple one-day diet plan.



NUTRITION KNOWLEDGE:



{context}





USER INFORMATION:



Age: {age}



Gender: {gender}



Height: {height} cm



Weight: {weight} kg



Activity Level: {activity}



aim: {aim}



Diet Type: {diet_type}



Food Allergy: {allergies}



Estimated BMI: {bmi}



Estimated BMR: {bmr} kcal/day



Estimated TDEE: {tdee} kcal/day



Estimated Daily Calorie Target:

{calories} kcal/day





Create the following:



1\. Breakfast

2\. Morning Snack

3\. Lunch

4\. Evening Snack

5\. Dinner





For every meal provide:



- Food

- Portion

- Approximate calories

- Approximate protein





IMPORTANT RULES:



\- Respect the user's diet type.

\- Do not recommend foods containing

&#x20; the stated allergy.

\- Use the provided nutrition knowledge

&#x20; when possible.

\- Keep the plan simple and practical.

\- Do not diagnose diseases.

\- Do not prescribe medicines.

\- Do not claim to cure diseases.

\- This is general wellness information,

&#x20; not medical advice."""
                    responce= client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role":"user",
                               "content":prompt}]
                    )
                    answer=responce.choices[0].message.content
                    st.markdown(answer)
                except:
                    st.error("RAG is not connected")
elif tab2:
    question=st.text_area("Ask About Heahth",
                 placeholder="eg.:Good Source of vegetatian protein")
    if st.button("Ask AI"):
        db=load_rag()
        docs=db.similarity_search(question,3)
        context="\n\n".join([doc.page_content for doc in docs])
        prompt=f"""You are an AI health and nutrition

assistant.
Use the following knowledge to answer
the user's question.
NUTRITION KNOWLEDGE:
{context}
USER QUESTION:
{question}
INSTRUCTIONS:
\- Answer clearly.
\- Keep the explanation beginner-friendly.
\- Use the provided knowledge when possible.
\- Do not invent medical facts.
\- Do not diagnose diseases.
\- Do not prescribe medicines.
\- Do not claim to cure diseases.
\- If the question concerns a serious
&#x20; medical problem, recommend consulting
&#x20; a qualified healthcare professional.
This application provides general health
and nutrition information for educational
and wellness purposes."""
        responce=client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role":"user",
                               "content":prompt}]
                )
        answer=responce.choice[0].message.content
        st.markdown(answer)
        
        
           
        
                

