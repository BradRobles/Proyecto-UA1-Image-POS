# Smart POS System & Business Intelligence Dashboard 🛒📊

**Team Members:**
* Karen Cardiel Olea
* Angeles Alejandra Cruz Legorreta
* Diego Jesús Loría Campos
* Brad Robles García

---

This project is a modern Point of Sale (POS) system that integrates a **Live Video Feed Machine Learning Model** for automated product scanning, alongside a comprehensive **Business Intelligence Dashboard** designed to aid decision-makers at multiple levels of an organization.

## 🎯 Project Goal
The primary objective of this project is to generate a visual aid for decision-makers based on a live video feed. We tackle streaming data information sourcing (identifying products via a webcam) and structure that gathered data into actionable information through innovative data visualization.

---

## 🤖 Machine Learning Integration
**Requirement:** *Employ at least 1 ML model.*

This system employs a **Computer Vision Classification Model** (trained via Google Teachable Machine) that runs locally using **TensorFlow.js**. 
* **Live Video Feed:** The system captures a continuous video stream from the user's webcam.
* **Real-time Inference:** The ML model analyzes the feed in real-time, recognizing products (e.g., Toys, Groceries) with a confidence threshold. 
* **Seamless Integration:** Once a product is confirmed by the AI, it automatically streams the data to the Python backend, appending the item to the operational POS ticket without manual intervention.

---

## 📈 3 Stages of Decision Making (Dashboard Visualization)
**Requirement:** *Give information for Operational, Tactic, and Strategic stages.*

The core of this project is the **Management Dashboard**, built using Python, Pandas, and **Plotly** for innovative and interactive visualizations. It processes the raw transaction data and translates it into the three required stages of decision making:

### 1. Operational Information (Day-to-Day)
* **Target Audience:** Cashiers and Shift Supervisors.
* **Goal:** Immediate action and daily tracking.
* **Visualizations & Metrics:** 
  * Real-time KPIs: Today's Revenue, Items Scanned, and Active Tickets.
  * **Live Transaction Log:** An expandable, detailed table showing the exact timestamp, product name, price, and scan source of every item sold. This allows supervisors to audit current shift operations and handle immediate customer queries.

### 2. Tactic Information (Medium-Term)
* **Target Audience:** Store Managers.
* **Goal:** Resource allocation and short-term planning.
* **Visualizations & Metrics:**
  * **Hourly Revenue Flow (Line Chart):** Maps sales activity across different hours of the day. *Decision Aid:* Allows the manager to optimize staff scheduling (e.g., assigning more cashiers during peak hours) and plan lunch breaks.
  * **Top Rotating Products (Bar Chart):** Ranks individual products by sales volume. *Decision Aid:* Instructs the manager on which specific items need urgent restocking from the warehouse to the storefront.

### 3. Strategic Information (Long-Term)
* **Target Audience:** Business Owners and C-Level Executives.
* **Goal:** Overall business direction, risk management, and market positioning.
* **Visualizations & Metrics:**
  * **Category Concentration (Pie Chart):** Groups individual items into macro-categories (e.g., Groceries vs. Collectibles vs. Toys). *Decision Aid:* Helps owners decide if the business should pivot its entire brand identity (e.g., transitioning fully into a collectible store if it yields 80% of revenue).
  * **Pareto Analysis 80/20 (Combined Bar & Line Chart):** Displays revenue per product alongside a cumulative percentage line. *Decision Aid:* Highlights catalog dependency. If a single product accounts for 70% of total revenue, executives know there is a severe supply-chain risk and must strategize to diversify their catalog.

---

## 🛠️ Tech Stack & Good Software Engineering Practices
* **Frontend/UI:** Streamlit (Python)
* **Data Visualization:** Plotly Express & Plotly Graph Objects (Innovative, interactive visualizations)
* **Machine Learning:** TensorFlow.js, HTML5 WebRTC
* **Data Handling:** Pandas, CSV persistence
* **Architecture:** Component-based architecture separating the frontend ML component (`scanner_component`), the business logic (`modulo_pos.py`), and the visualization engine (`modulo_dashboard.py`).

## 🚀 How to Run the Project
1. **Start the ML Model Server:**
   This serves the TensorFlow.js model files locally.
   ```bash
   python3 server.py
   ```
2. **Start the POS Application:**
   ```bash
   streamlit run main.py
   ```
3. Open your browser at `http://localhost:8501`.
