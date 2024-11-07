import streamlit as st
from streamlit_option_menu import option_menu
import Recommend
import ReforUser
import Web
class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        with st.sidebar:
            app = option_menu(
                menu_title='Movies Recommendation ',
                options=['Movies','Recommend','User'],
                default_index=1,
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
                    "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )
        if app == "Movies":
            Web.main_page()
        if app =="Recommend":
            Recommend.main_page()
        if app == "User":
            ReforUser.app()
    run()