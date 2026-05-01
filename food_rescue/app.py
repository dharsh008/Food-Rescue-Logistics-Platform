import streamlit as st
from utils.helpers import load_json, save_json
import base64
from datetime import datetime

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Food Rescue Platform", layout="wide")

# -------------------- LOAD DATA --------------------
users = load_json("data/users.json")
food_list = load_json("data/food.json")
orphanage_requests = load_json("data/orphanage_requests.json")

# -------------------- SESSION STATE --------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# -------------------- STYLES --------------------
st.markdown("""
<style>
.stButton>button {
    width: 100%;
    height: 3em;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.page = "welcome"
    st.rerun()


# ====================================================
# -------------------- WELCOME PAGE ------------------
# ====================================================
if st.session_state.page == "welcome":
    col1, col2 = st.columns([1.2,1])
    with col1:
        st.image("assets/ngo.jpg", use_container_width=True)
    with col2:
        st.markdown("## Welcome to Food Rescue Platform")
        st.markdown("### Save food. Feed people. Protect the planet 🌍")
        if st.button("Sign In"):
            st.session_state.page = "login"
        if st.button("Sign Up"):
            st.session_state.page = "signup"

# ====================================================
# -------------------- SIGN UP PAGE ------------------
# ====================================================
elif st.session_state.page == "signup":
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.image("assets/ngo.jpg", use_container_width=True)
    with col2:
        st.markdown("## Create Account")
        name = st.text_input("Name")
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):
            if name and password:
                users.append({"name": name, "password": password, "role": "Donor"})
                save_json("data/users.json", users)
                st.success("Account created! Please login.")
                st.session_state.page = "login"
            else:
                st.error("Please fill all fields")

        if st.button("Back"):
            st.session_state.page = "welcome"

# ====================================================
# -------------------- LOGIN PAGE --------------------
# ====================================================
elif st.session_state.page == "login":
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.image("assets/ngo.jpg", use_container_width=True)

    with col2:
        st.markdown("## Sign In")
        name = st.text_input("Name")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = next(
                (u for u in users if u.get("name") == name and u.get("password") == password),
                None
            )

            if user:
                st.session_state.user = user

                role = user.get("role", "").strip().capitalize()

                if role == "Donor":
                    st.session_state.page = "donor_dashboard"
                elif role == "Ngo":
                    st.session_state.page = "ngo_dashboard"
                elif role == "Volunteer":
                    st.session_state.page = "volunteer_dashboard"
                elif role == "Orphanage":
                    st.session_state.page = "orphanage_dashboard"

                st.rerun()
            else:
                st.error("Invalid credentials")

        if st.button("Back"):
            st.session_state.page = "welcome"


# ====================================================
# ---------------- DONOR DASHBOARD ------------------
# ====================================================
elif st.session_state.page == "donor_dashboard":
    donor_name = st.session_state.user["name"]
    st.title("A small donation can create a big change!! Give what you can.  Someone is waiting for your help")
    st.subheader(f"Welcome **{donor_name}** 👋")

    if st.button("Logout"):
        st.session_state.page = "welcome"

    st.markdown("---")
    st.subheader("Post Food Donation")

    with st.form("post_food"):
        org_name = st.text_input("Organization / Hotel Name")
        phone = st.text_input("Mobile Number")
        address = st.text_area("Pickup Address")
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity (kg)", min_value=1)
        expiry_time = st.time_input("Expiry Time")
        food_photo = st.file_uploader("Upload Food Photo", type=["jpg", "png", "jpeg"])
        submit = st.form_submit_button("Post Food")

        if submit:
            current_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
            photo_url = None
            if food_photo:
                photo_url = "data:image/png;base64," + base64.b64encode(food_photo.read()).decode()

            food_list.insert(0, {
                "food_id": len(food_list) + 1,
                "donor_name": donor_name,
                "organization": org_name,
                "phone": phone,
                "address": address,
                "food_name": food_name,
                "quantity_kg": quantity,
                "expiry_time": expiry_time.strftime("%I:%M %p"),
                "photo": photo_url,
                "status": "Posted",
                "posted_at": current_time,
                "status_history": [{"status": "Posted", "time": current_time}]
            })

            save_json("data/food.json", food_list)
            st.success("Food posted successfully!")

    st.markdown("---")
    st.subheader("My Previous Donations")

    for food in food_list:
        if food.get("donor_name") == donor_name:
            st.write(f"🍽 **{food['food_name']}**")
            st.write(f"🕒 Posted at: {food.get('posted_at')}")

            if food.get("photo"):
                st.image(food["photo"], width=200)
           


            if st.button(f"View Details #{food['food_id']}", key=f"details_{food['food_id']}"):
                st.subheader("📦 Food Tracking Timeline")
                for h in food.get("status_history", []):
                    st.write(f"✅ {h['status']} — 🕒 {h['time']}")
            st.markdown("---")
            

# ====================================================
# ---------------- NGO DASHBOARD ---------------------
# ====================================================
if st.session_state.page == "ngo_dashboard":

    ngo_name = st.session_state.user["name"]

    st.title("Hunger ends where compassion begins!!  Service to humanity is service to life")

    col_logout, col_space = st.columns([1, 6])
    with col_logout:
        if st.button("Logout"):
            logout()

    # ================= ASSIGN ROLE SECTION =================
    st.markdown("### 🛠 Assign Role ")

    with st.expander("➕ Create Volunteer / Orphanage Login"):
        new_name = st.text_input("Username", key="new_user_name")
        new_password = st.text_input("Password", type="password", key="new_user_pwd")
        new_role = st.selectbox(
            "Assign Role",
            ["Volunteer", "Orphanage"],
            key="new_user_role"
        )

        if st.button("Create User"):
            if new_name and new_password:
                users = load_json("data/users.json")

                if any(u["name"] == new_name for u in users):
                    st.error("User already exists ❌")
                else:
                    users.append({
                        "name": new_name,
                        "password": new_password,
                        "role": new_role
                    })
                    save_json("data/users.json", users)
                    st.success(f"{new_role} account created successfully ✅")
            else:
                st.error("Please fill all fields")

    st.markdown("---")

    # ✅ LOAD DATA FROM CORRECT FILES
    food_list = load_json("data/food.json")                     # DONOR DATA ONLY
    orphanage_list = load_json("data/orphanage_requests.json")  # ORPHANAGE DATA ONLY

    tab1, tab2 , tab3= st.tabs(["🏨 HOTEL DETAILS", "🏠 ORPHANAGE DETAILS", "🏠Assign Volunteer to Orphanage"])
# ====================================================
    # 🏨 HOTEL DETAILS — HOTEL ONLY
    # ====================================================
    with tab1:
     donor_found = False

     for food in food_list:

        if not all(k in food for k in ["food_id", "food_name", "donor_name"]):
            continue

        donor_found = True

        if food["status"] == "Posted" or food["status"].startswith(
            ("Accepted", "Pick up is confirmed", "Food collected", "Picked", "Delivered")
        ):
            st.markdown(
                f"""
                <div style="border-radius:15px;padding:20px;
                background-color:#f9f9f9;box-shadow:0px 4px 10px rgba(0,0,0,0.1);">
                <h4>🍽 {food['food_name']}</h4>
                <p><b>Donor:</b> {food['donor_name']}</p>
                <p><b>Address:</b> {food['address']}</p>
                <p><b>Phone:</b> {food['phone']}</p>
                <p><b>Quantity:</b> {food['quantity_kg']} kg</p>
                <p><b>Posted:</b> {food.get('posted_at', 'N/A')}</p>
                <p><b>Expiry:</b> {food['expiry_time']}</p>
                <p><b>Status:</b> 🟢 {food['status']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            # ✅ SHOW FOOD IMAGE IF AVAILABLE
            if food.get("photo"):
              st.image(food["photo"], width=250)


            if food["status"] == "Posted":
                if st.button(
                    f"✅ Accept Food #{food['food_id']}",
                    key=f"accept_food_{food['food_id']}"
                ):
                    food["status"] = f"Accepted by NGO ({ngo_name})"
                    food.setdefault("history", []).append({
                        "status": "Accepted by NGO",
                        "time": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                    })
                    save_json("data/food.json", food_list)
                    st.success("Food accepted successfully ✅")
                    st.rerun()

    if not donor_found:
        st.info("No hotel food donations available")

    
    # ====================================================
# 🏠 ORPHANAGE DETAILS — ORPHANAGE ONLY
# ====================================================
    with tab2:

     if not orphanage_list:
        st.info("No orphanage requests available")

     for idx, req in enumerate(orphanage_list):

        if "history" not in req:
            req["history"] = []

        st.markdown(
            f"""
            <div style="border-radius:15px;padding:20px;
            background-color:#eef6ff;box-shadow:0px 4px 10px rgba(0,0,0,0.1);">
            <h4>🏠 {req['orphanage_name']}</h4>
            <p><b>Address:</b> {req['address']}</p>
            <p><b>Phone:</b> {req['phone']}</p>
            <p><b>People:</b> {req['people']}</p>
            <p><b>Meal:</b> {req['meal_type']}</p>
            <p><b>Food Needed:</b> {req['quantity']} kg</p>
            <p><b>Date:</b> {req['date']}</p>
            <p><b>Status:</b> 🔵 {req['status']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if req["status"].lower() in ["submitted", "pending"]:
            if st.button(f"✔ Accept Request #{idx + 1}", key=f"accept_orph_{idx}"):
                req["status"] = "Accepted by NGO"
                req["history"].append({
                    "status": f"Accepted by NGO ({ngo_name})",
                    "time": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                })
                save_json("data/orphanage_requests.json", orphanage_list)
                st.success("Orphanage request accepted ✅")
                st.rerun()

      # ==========================================================
    # 🏠 ASSIGN VOLUNTEER TO ORPHANAGE — NEW FEATURE
    # ==========================================================

    with tab3:
        

        assignments = load_json("data/assignments.json")
        users = load_json("data/users.json")

        if "show_assign_form" not in st.session_state:
            st.session_state.show_assign_form = True

        # 🔘 MAIN BUTTON (FORM HIDDEN BY DEFAULT)
       # if st.button("✳ Assign Orphanage to Volunteer"):
         #   st.session_state.show_assign_form = True

        # 📝 ASSIGNMENT FORM (VISIBLE ONLY AFTER CLICK)
        if st.session_state.show_assign_form:

            orphanage = st.selectbox(
                "Select Orphanage",
                orphanage_list,
                format_func=lambda x: x["orphanage_name"]
            )

            volunteers = [u["name"] for u in users if u["role"] == "Volunteer"]

            volunteer = st.selectbox("Select Volunteer", volunteers)

            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity (kg)", min_value=1)
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner"])
            phone=st.number_input("Phone")
            address=st.text_input("Address")

            if st.button("✅ Confirm Assignment"):
                assignments.append({
                    "ngo": ngo_name,
                    "volunteer": volunteer,
                    "orphanage": orphanage["orphanage_name"],
                    "food_name": food_name,
                    "quantity": quantity,
                    "meal_type": meal_type,
                    "phone":phone,
                    "address":address,
                    "history": [
                        {
                            "status": "Assigned by NGO",
                            "time": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                        }
                    ]
                })

                save_json("data/assignments.json", assignments)
                st.success("Volunteer assigned successfully ✅")
                st.session_state.show_assign_form = False
                st.rerun()

        # 📍 TRACK HISTORY (VISIBLE ONLY AFTER ASSIGNMENT)
        st.markdown("### 📍 Track History")

        ngo_assignments = [a for a in assignments if a["ngo"] == ngo_name]

        if not ngo_assignments:
            st.info("No assignments yet")
        else:
            for idx, a in enumerate(ngo_assignments):
                if st.button(
                    f"📍 Track {a['orphanage']} → {a['volunteer']}",
                    key=f"track_{idx}"
                ):
                    for h in a["history"]:
                        st.write(f"✅ {h['status']} — 🕒 {h['time']}")



# ====================================================
# --------------- ORPHANAGE DASHBOARD ----------------
# ====================================================
elif st.session_state.page == "orphanage_dashboard":

    from datetime import datetime

    orphan_user = st.session_state.user["name"]

    st.title("Care you can trust, love you can feel from NGO !!  NGO is here for you—today and always. 🏠")

    if st.button("Logout"):
        logout()

    # --------- SESSION STATE INIT ----------
    if "active_history_index" not in st.session_state:
        st.session_state.active_history_index = None

    # --------- LOAD DATA ----------
    orphanage_requests = load_json("data/orphanage_requests.json")
    assignments = load_json("data/assignments.json")

    # --------- REQUEST FORM ----------
    with st.form("orphan_form"):
        name = st.text_input("Orphanage Name")
        address = st.text_area("Address")
        phone = st.text_input("Phone Number")
        people = st.number_input("No. of People Need Food", min_value=1)
        quantity = st.number_input("Quantity of Food Required (kg)", min_value=1)
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner"])
        date = st.date_input("Date Required")
        submit = st.form_submit_button("Submit")

        if submit:
            current_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

            orphanage_requests.append({
                "orphanage_user": orphan_user,
                "orphanage_name": name,
                "address": address,
                "phone": phone,
                "people": people,
                "quantity": quantity,
                "meal_type": meal_type,
                "date": str(date),
                "status": "Submitted",
                "history": [
                    {
                        "status": "Submitted",
                        "time": current_time
                    }
                ]
            })

            save_json("data/orphanage_requests.json", orphanage_requests)
            st.success("Request submitted successfully ✅")
            st.rerun()

    # --------- TRACKING SECTION ----------
    st.markdown("---")
    st.subheader("📍 My Requests Status & Tracking")

    for idx, req in enumerate(orphanage_requests):
        if req.get("orphanage_user") != orphan_user:
            continue

        st.markdown(f"### 🍽 {req['meal_type']} | 📅 {req['date']}")

        # Track button
        if st.button("📜 Track History", key=f"track_{idx}"):
            st.session_state.active_history_index = idx

        # Show history only when clicked
        if st.session_state.active_history_index == idx:

            # --------- ENSURE HISTORY ----------
            if "history" not in req:
                req["history"] = []

            # --------- DISPLAY ORPHANAGE + NGO HISTORY ----------
            if not req["history"]:
                st.info("No updates yet.")
            else:
                for h in req["history"]:
                    st.write(f"✅ **{h['status']}** — ⏰ {h['time']}")

            # --------- DISPLAY VOLUNTEER DELIVERY HISTORY ----------
            for assign in assignments:
                if (
                    assign.get("orphanage") == req.get("orphanage_name")
                    and assign.get("meal_type") == req.get("meal_type")
                ):
                    for h in assign.get("history", []):
                        st.write(
                            f"🚚 **{h['status']}**  \n"
                            f"👤 Volunteer: **{assign.get('volunteer', 'N/A')}**  \n"
                            f"⏰ {h['time']}"
                        )

        st.markdown("---")

# ====================================================
# --------------- VOLUNTEER DASHBOARD ----------------
# ==================================================
elif st.session_state.page == "volunteer_dashboard":

    volunteer_name = st.session_state.user["name"]

    st.title("Volunteers turn compassion into action !!  Service is the rent we pay for living ")
    st.write(f"Welcome **{volunteer_name}** 💙")

    if st.button("Logout"):
        st.session_state.page = "welcome"

    st.markdown("---")

    # ====================================================
    # 🍽 EXISTING FOOD PICKUP FLOW (UNCHANGED)
    # ====================================================
    food_list = load_json("data/food.json")

    tasks = [
        f for f in food_list
        if f.get("status", "").startswith("Accepted by NGO")
        or f.get("status") == f"Pick up is confirmed by Volunteer ({volunteer_name})"
    ]

    if not tasks:
        st.info("No pickup or collection tasks available right now.")
    else:
        for food in tasks:
            st.write(f"🍽 **{food.get('food_name')}**")
            st.write(f"📍 {food.get('address', 'N/A')}")
            st.write(f"📞 {food.get('phone', 'N/A')}")
            st.write(f"👤 Donor: {food.get('donor_name', 'N/A')}")
            st.write(f"🏢 Organization: {food.get('organization', 'N/A')}")
            st.write(f"⏰ Expiry Time: {food.get('expiry_time', 'N/A')}")
            st.write(f"📌 Status: {food.get('status')}")

            if food.get("photo"):
                st.image(food["photo"], width=220)

            current_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

            if food["status"].startswith("Accepted by NGO"):
                if st.button(f"📦 Pick Up Food #{food['food_id']}", key=f"pickup_{food['food_id']}"):
                    food["status"] = f"Pick up is confirmed by Volunteer ({volunteer_name})"
                    food["status_history"].append({
                        "status": food["status"],
                        "time": current_time
                    })
                    save_json("data/food.json", food_list)
                    st.success("Pick up confirmed ✅")
                    st.rerun()

            elif food["status"] == f"Pick up is confirmed by Volunteer ({volunteer_name})":
                if st.button(f"🥡 Collected Food #{food['food_id']}", key=f"collect_{food['food_id']}"):
                    food["status"] = f"Food collected by Volunteer ({volunteer_name})"
                    food["status_history"].append({
                        "status": food["status"],
                        "time": current_time
                    })
                    save_json("data/food.json", food_list)
                    st.success("Food collected successfully 🍽")
                    st.rerun()

            st.markdown("---")

    # ====================================================
    # 🏠 NGO ASSIGNED ORPHANAGE DELIVERY (FIXED)
    # ====================================================
    st.markdown("## 🚚 NGO Assigned Delivery")

    assignments = load_json("data/assignments.json")
    orphanage_requests = load_json("data/orphanage_requests.json")

    my_assignments = [
        a for a in assignments
        if a.get("volunteer") == volunteer_name
        and not any(
            h.get("status") == "Delivered successfully to orphanage"
            for h in a.get("history", [])
        )
    ]

    if not my_assignments:
        st.info("No delivery assigned by NGO yet.")
    else:
        for idx, task in enumerate(my_assignments):

            orphanage_name = task.get("orphanage", "N/A")
            orphanage_address = "N/A"
            orphanage_phone = "N/A"

            # 🔍 FETCH ADDRESS & PHONE FROM ORPHANAGE REQUESTS
            for o in orphanage_requests:
                if o.get("orphanage_name") == orphanage_name:
                    orphanage_address = o.get("address", "N/A")
                    orphanage_phone = o.get("phone", "N/A")
                    break

            st.markdown(
                f"""
                <div style="
                    border-radius:15px;
                    padding:20px;
                    background-color:#f4fff4;
                    box-shadow:0px 4px 10px rgba(0,0,0,0.1);
                ">
                <h4>🏠 Orphanage: {orphanage_name}</h4>
                <p><b>Address:</b> {orphanage_address}</p>
                <p><b>Phone:</b> {orphanage_phone}</p>

                <p><b>Food:</b> {task.get('food_name')}</p>
                <p><b>Quantity:</b> {task.get('quantity')} kg</p>
                <p><b>Meal:</b> {task.get('meal_type')}</p>
                <p><b>Assigned by NGO:</b> {task.get('ngo')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)

            # ✅ DELIVERY ACCEPTED
            with col1:
                if st.button("✅ Delivery Accepted", key=f"delivery_accept_{idx}"):
                    task["history"].append({
                        "status": f"Delivery accepted by {volunteer_name}",
                        "time": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                    })
                    save_json("data/assignments.json", assignments)
                    st.success("Delivery accepted successfully ✅")
                    st.rerun()

            # 📦 DELIVERED SUCCESSFULLY → REMOVE FROM VIEW
            with col2:
                if st.button("📦 Delivered Successfully", key=f"delivery_done_{idx}"):
                    task["history"].append({
                        "status": "Delivered successfully to orphanage",
                        "time": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                    })
                    save_json("data/assignments.json", assignments)
                    st.success("Delivery completed 🎉")
                    st.rerun()

            st.markdown("---")