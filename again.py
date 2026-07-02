# import streamlit as st

# items = [
#     "Apple",
#     "Application",
#     "Apricot",
#     "Banana",
#     "Blueberry",
#     "Cherry",
#     "Date"
# ]

# search = st.text_input("Search")

# if search:
#     matches = [
#         item for item in items
#         if item.lower().startswith(search.lower())
#     ]

#     if matches:
#         selected = st.selectbox(
#             "Suggestions",
#             matches,
#             label_visibility="collapsed"
#         )

#         if st.button("Use"):
#             st.write(f"Selected: {selected}")

# # import streamlit as st

# # items = [
# #     "Apple",
# #     "Application",
# #     "Apricot",
# #     "Banana",
# #     "Blueberry",
# #     "Cherry",
# #     "Date"
# # ]

# # # store selected item
# # if "selected" not in st.session_state:
# #     st.session_state.selected = ""

# # search = st.text_input("Search", value=st.session_state.selected)

# # if search:
# #     matches = [
# #         item for item in items
# #         if item.lower().startswith(search.lower())
# #     ]

# #     if matches:
# #         st.write("Suggestions:")

# #         # Google-like clickable suggestions
# #         for m in matches:
# #             if st.button(m, key=m):
# #                 st.session_state.selected = m
# #                 st.rerun()

# # # show final selection
# # if st.session_state.selected:
# #     st.success(f"Selected: {st.session_state.selected}")

import streamlit as st
 
items = [
    "Apple",
    "Application",
    "Apricot",
    "Banana",
    "Blueberry",
    "Cherry",
    "Date"
]
 
search = st.text_input("Search")
 
if search:
    matches = [
        item for item in items
        if item.lower().startswith(search.lower())
    ]
 
    if matches:
        selected = st.radio(
            "Suggestions",
            matches,
            label_visibility="collapsed"
        )
 
        if st.button("Use"):
            st.write(f"Selected: {selected}")