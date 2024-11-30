<p align="center">
  <img src="assets/logo.png" alt="Project Logo" width="500">
</p>

[![DOI](https://zenodo.org/badge/882147579.svg)](https://doi.org/10.5281/zenodo.14027393)

<!-- [![GitHub Release](https://img.shields.io/badge/release-v6.0.11.1-blue)](https://github.com/DFY-NCSU/CoinCanvas) -->
[![Backend Tests & Coverage](https://github.com/DFY-NCSU/CoinCanvas/actions/workflows/test_backend.yml/badge.svg)](https://github.com/DFY-NCSU/CoinCanvas/actions/workflows/test_backend.yml)
[![codecov](https://codecov.io/gh/DFY-NCSU/CoinCanvas/branch/main/graph/badge.svg?token=Gi5Jh3vn8Q)](https://codecov.io/gh/DFY-NCSU/CoinCanvas/tree/main)
[![Flake8 Lint](https://github.com/DFY-NCSU/CoinCanvas/actions/workflows/flake8.yml/badge.svg)](https://github.com/DFY-NCSU/CoinCanvas/actions/workflows/flake8.yml)
[![Syntax Check](https://github.com/DFY-NCSU/CoinCanvas/actions/workflows/syntax.yml/badge.svg)](https://github.com/DFY-NCSU/CoinCanvas/actions/workflows/syntax.yml)
[![Python Style Checker](https://github.com/DFY-NCSU/CoinCanvas/actions/workflows/style.yml/badge.svg)](https://github.com/DFY-NCSU/CoinCanvas/actions/workflows/style.yml)
<!-- [![codecov](https://codecov.io/gh/DFY-NCSU/CoinCanvas/branch/main/graph/badge.svg?token=oJrKEnEGwP)](https://codecov.io/gh/DFY-NCSU/CoinCanvas/tree/main) -->

<a href="https://github.com/DFY-NCSU/CoinCanvas/blob/main/LICENSE.md"><img alt="GitHub license" src="https://img.shields.io/github/license/DFY-NCSU/CoinCanvas"></a>
<a href="https://github.com/DFY-NCSU/CoinCanvas/forks"><img alt="GitHub forks" src="https://img.shields.io/github/forks/DFY-NCSU/CoinCanvas"></a>
<a href="https://github.com/DFY-NCSU/CoinCanvas/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/DFY-NCSU/CoinCanvas"></a>
<a href="https://github.com/DFY-NCSU/CoinCanvas/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/DFY-NCSU/CoinCanvas"></a>
<a href="https://github.com/DFY-NCSU/CoinCanvas/issues?q=is%3Aissue+is%3Aclosed"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed/DFY-NCSU/CoinCanvas">
<a href="https://github.com/DFY-NCSU/CoinCanvas/pulls"><img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/DFY-NCSU/CoinCanvas">
<a href="https://github.com/DFY-NCSU/CoinCanvas/pulls?q=is%3Apr+is%3Aclosed"><img alt="GitHub closed pull requests" src="https://img.shields.io/github/issues-pr-closed/DFY-NCSU/CoinCanvas">
<a href="https://github.com/DFY-NCSU/CoinCanvas/discussions"><img alt="GitHub discussion channel" src="https://img.shields.io/github/discussions/DFY-NCSU/CoinCanvas">


# 💡 Transform Your Financial Story with CoinCanvas

Ever stared at your bank statement wondering where your money went? You're not alone. CoinCanvas transforms the complex world of personal finance into a clear, visual story. Whether you're splitting expenses with roommates, planning a group vacation, or working toward personal financial goals, CoinCanvas makes it simple and intuitive.

![](assets/intro.jpg)

## 🎨 Why CoinCanvas?

Think of your finances as a blank canvas. Each expense is a brushstroke, each saving goal a color, each shared expense a collaborative art piece. CoinCanvas is your smart easel, helping you create a masterpiece of financial clarity.

## 👥 Who Should Use CoinCanvas?

- **Young Professionals** balancing career growth with social life
- **Students** managing shared housing expenses
- **Families** coordinating household budgets
- **Freelancers** tracking variable income and expenses
- **Group Travelers** organizing trip expenses
- **Anyone** seeking financial clarity and control

## ✨ Key Features

- **🗓️ Flexible Time Recording**  
  Unlike other expense trackers that require immediate input, CoinCanvas lets you record expenses whenever it's convenient. Whether it's from last week's dinner or today's coffee, our date selection feature ensures your financial records stay accurate and complete.

- **💻 True Cross-Platform Experience**  
  CoinCanvas isn't just "cross-platform capable" - it's truly cross-platform optimized. Access and manage your expenses seamlessly across web, mobile, and desktop platforms with a consistent, user-friendly interface.

- **🤖 AI-Powered Financial Intelligence**  
  Exclusive to CoinCanvas: Advanced AI analysis that transforms your spending data into actionable insights:
  - Personalized spending pattern analysis
  - Smart budget recommendations
  - Predictive expense forecasting
  - Anomaly detection for unusual spending
  - AI-driven saving opportunities
  
  **More AI-Driven Features**

  - **📝 Smart Budgeting Advice**  
  Personalized recommendations based on your patterns

  - **💡 Savings Opportunities**  
    AI-detected areas for cost reduction

  - **🔮 Expense Prediction**  
    Anticipate and prepare for future expenses

  - **⚠️ Anomaly Detection**  
    Smart alerts for unusual spending

  - **🎯 Goal Setting**  
    AI-assisted realistic financial targets

## 🚀 Quick Start

### Backend Setup
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start the server
uvicorn backend.app.main:app --reload

# Access API documentation
open http://127.0.0.1:8000/docs
```

### Frontend Setup
```bash
# enter the working directory
cd frontend

# Ensure Flutter is installed
flutter doctor

# Get dependencies
flutter pub get

# Run the application
flutter run -d chrome
```

### Demo Database

Download our demo database from [Google Drive](https://drive.google.com/file/d/1tA9uxEWfziiNkTtT1AWyrvG4DrXnj3Te/view?usp=sharing) to try out all features immediately.

To login, you can use `email=email@test.com` and `password=pass123`.

## 🔮 Future Map: Expanding AI-Based Functions

### **Phase 1: Personalized Insights and Assistance**

1. **💬 AI-Powered Financial Chatbot**
   - **Description**: Offer a conversational assistant that provides real-time financial advice, answers queries, and offers tips based on user data.
   - **Benefits**:
     - **Engagement**: Encourages users to interact more deeply with their finances.
     - **Support**: Acts as a personal financial advisor available 24/7.

2. **📊 Dynamic Financial Planning**
   - **Description**: Utilize AI to help users create and adjust long-term financial plans, adapting to changes in income, expenses, or life events.
   - **Benefits**:
     - **Flexibility**: Plans evolve with the user's financial situation.
     - **Goal Alignment**: Keeps users focused on their objectives.

3. **🧘 Emotional Spending Analysis**
   - **Description**: Analyze spending habits in relation to emotional states, possibly integrating with wellness apps to provide context.
   - **Benefits**:
     - **Awareness**: Helps users understand the impact of emotions on spending.
     - **Behavioral Change**: Encourages healthier financial habits.

### **Phase 2: Predictive Analytics and Security**

1. **🔮 Predictive Financial Health Score**
   - **Description**: Assign a dynamic score predicting financial wellness based on current spending, saving patterns, and economic indicators.
   - **Benefits**:
     - **Motivation**: Users can track and improve their score.
     - **Insight**: Provides a snapshot of financial trajectory.

2. **🛡️ AI-Driven Fraud Detection**
   - **Description**: Implement algorithms that detect unusual activity, alerting users to potential fraudulent transactions.
   - **Benefits**:
     - **Security**: Protects users from unauthorized expenses.
     - **Trust**: Enhances the app's credibility.

3. **💰 Investment Insights**
   - **Description**: Provide personalized investment suggestions based on user financial data and market trends.
   - **Benefits**:
     - **Growth Opportunities**: Introduces users to potential investments.
     - **Education**: Enhances financial literacy.

### **Phase 3: Social Features and Gamification**

1. **👥 Expense Sharing and Group Tracking**
    - **Description**: Facilitate shared expenses among friends or family, with AI managing splits and tracking group spendings.
    - **Benefits**:
      - **Collaboration**: Simplifies managing joint expenses.
      - **Transparency**: Keeps all parties informed.

2. **🏆 Gamification Elements**
    - **Description**: Introduce challenges, rewards, and achievements for meeting financial goals, powered by AI to keep content fresh and engaging.
    - **Benefits**:
      - **Engagement**: Makes financial management fun.
      - **Incentivization**: Encourages users to stay on track.

3. **📝 AI-Based Bill Negotiation Suggestions**
    - **Description**: Analyze recurring bills and suggest opportunities to negotiate better rates or find more affordable alternatives.
    - **Benefits**:
      - **Cost Savings**: Helps users reduce expenses.
      - **Empowerment**: Provides actionable advice.
  
### **Phase 4: Integration and Education**

1. **🔗 Integration with Financial Institutions**
    - **Description**: Allow users to connect bank accounts, credit cards, and other financial services for automatic data import and analysis.
    - **Benefits**:
      - **Convenience**: Streamlines expense tracking.
      - **Comprehensive View**: Gives users a complete financial picture.

2. **📚 Personalized Financial Education**
    - **Description**: Deliver tailored educational content based on the user's financial behavior and knowledge gaps.
    - **Benefits**:
      - **Learning**: Enhances users' financial literacy.
      - **Relevance**: Provides information when it's most needed.

3. **⏰ Smart Bill Management**
    - **Description**: AI tracks upcoming bills, predicts amounts due, and sends reminders or automates payments.
    - **Benefits**:
      - **Organization**: Prevents missed payments.
      - **Cash Flow Management**: Assists in planning expenses.

### **Phase 5: Future Innovations**

1. **🌐 Multi-Currency and International Support**
    - **Description**: Support multiple currencies with AI handling conversions and international financial regulations.
    - **Benefits**:
      - **Global Reach**: Attracts an international user base.
      - **Convenience**: Helps users who travel or transact globally.

2. **🤝 Integration with Other Services**
    - **Description**: Connect with e-commerce, subscription services, and utilities for seamless expense tracking.
    - **Benefits**:
      - **Automation**: Further reduces manual entry.
      - **Accuracy**: Ensures all expenses are captured.

3. **⚡ Real-Time Financial Market Updates**
    - **Description**: Provide live updates on stock markets, interest rates, and economic news relevant to the user's financial interests.
    - **Benefits**:
      - **Timeliness**: Keeps users informed.
      - **Decision Support**: Assists with timely financial decisions.


## 🌟 Success Stories

> "CoinCanvas turned our house's expense management from a monthly headache into a seamless experience. Now we can focus on being roommates instead of accountants!" - Maowen, 23

> "Setting and tracking financial goals has never been easier. I'm finally making progress on my savings goals!" - Hannah, 27

## 📚 Documentation

- [Installation Guide](docs/INSTALL.md)
- [User Tutorial](docs/MiniTutorial.md)
- [API Documentation](http://127.0.0.1:8000/docs) (needs the backend to be running)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Community & Support

- [Report Issues](https://github.com/DFY-NCSU/CoinCanvas/issues/new?assignees=&labels=&projects=&template=bug_report.md&title=)
- [Feature Requests](https://github.com/DFY-NCSU/CoinCanvas/issues/new?assignees=&labels=&projects=&template=feature_request.md&title=)
- [Discussions](https://github.com/DFY-NCSU/CoinCanvas/discussions)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>Your financial masterpiece begins with a single stroke.</i><br>
  Start painting your financial future today with CoinCanvas.
</p>