# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
from st_pages import Page, show_pages, add_page_title

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="WUNDER data checker",
        page_icon="👋",
    )

    # Specify what pages should be shown in the sidebar, and what their titles 
    # and icons should be
    show_pages(
        [
            Page("Hello.py", "Home", "🏠"),
            Page("pages/1_radiation_data_checker.py", "Radiation", ":sun:"),
        ]
    )

    st.write("# Welcome to the WUNDER data checker! 👋")

    st.sidebar.success("Select a group of variables you like to explore.")

    st.markdown(
        """
        With this app you are able to quickly check the data gathered within the WUNDER project on a near real time basis
        **👈 Select a group of variables** to start checking.
        ### More information about the WUNDER project can be found on the offical webpage:
        - https://www.itc.nl/about-itc/scientific-departments/water-resources/wunder-project/
        ### Contact?
        - Liduin Bos-Burgering (TU Delft, Deltares)
        - Miriam Coenders (TU Delft)
        - Gijs Vis (TU Delft)
        - Bob Su (UTwente)
        - Yijian Zeng (UTwente)
    """
    )


if __name__ == "__main__":
    run()
