# AuditCard

`AuditCards` serve a special purpose in `OpsML` and can be viewed as a card that contains governance, compliance, and ethical information about a particular model and its associated assets. Importantly, information contained in an `AuditCard` can be used be governing bodies and stakeholders to assess and approve a model for production.

`AuditCards` are created by instantiating the `AuditCard` class and passing in the required arguments. When working in python, you can list and answer questions as part of your normal workflow. However, the easiest and most intuitive way to create and update `AuditCards` is through the `OpsML` UI (Audit tab). 

## Code Example

```python
from opsml.registry import AuditCard, CardRegistry

... # create model and data cards

auditcard = AuditCard(
    name="linear-regressor-audit",
    team="my_team", 
    user_email="user_email"
)

# add modelcard to auditcard
auditcard.add_card(modelcard)


# list questions
auditcard.list_questions()

# list by section
card.list_questions(section="business")

# answer question
card.answer_question(section="business", question_nbr=1, response="response")

# register
audit_registry = CardRegistry("audit")
audit_registry.register_card(auditcard)
```

## AuditCard Audit Sections

### Business

: In the Business Understanding section, various important aspects are addressed to clarify the purpose and objectives of an AI application. These questions help provide a comprehensive understanding of the business context:

1. **Business Objectives**: The product owner's goals and intentions are identified. This helps in understanding what they aim to achieve with the AI application.

2. **Business Requirements**: The specific requirements set by the product owner for the application are outlined. This includes factors like development costs, operational costs, staffing needs, and anticipated savings.

3. **KPIs (Key Performance Indicators)**: The KPIs that the product owner intends to improve with the application are determined. This includes the rationale behind selecting specific KPIs and how they will be measured.

4. **Business Processes**: The impact of the application on various business processes is assessed. This involves understanding the criticality of affected processes, their relationships, and the significance of the application within these processes.

5. **Driver for Application Introduction**: The underlying reasons that drove the decision to develop the application are identified. This can include factors like regulatory mandates, cost considerations, or the need to address new challenges.

6. **Framework Conditions**: The readiness of the product owner to efficiently operate the system is evaluated. This includes factors such as staffing, infrastructure, user support, and quality assurance.

7. **Monetary Benefits**: The financial benefits and cost-savings expected from using the application are examined to determine their reasonableness and feasibility.

8. **Qualifiable and Strategic Benefits**: Any non-financial benefits derived from the application, such as improved processes or strategic advantages, are documented, along with their measurement capabilities.

9. **Value for Money**: The evaluation of the system's cost-effectiveness and efficiency is checked to ensure compliance with recognized methods and requirements.

10. **Risk Analysis**: The risks associated with the application, data preparation, and the processes it encompasses are analyzed. This includes identifying which risks to mitigate and which ones to accept, and assessing whether the benefits outweigh the risks and align with regulations.

These questions help stakeholders gain a clear understanding of the business context, goals, and risks associated with the AI application, facilitating better decision-making and project management.


### Data Understanding

: In the Data Understanding section, we delve into various aspects of data that are essential for the successful operation of the application. Here are concise descriptions of the key questions and their purposes:

1. **Data Processed by the Application**: This question seeks to understand the types of data that the application works with, encompassing both the data it receives as input and the data it generates as output. It's about identifying the information the application handles.

2. **Data Sources**: To gain insights into the reliability and relevance of data, it's important to identify the approved data sources, their freshness, reliability, and whether they are mandated to provide information.

3. **Technical/Operational Criteria for Data Selection**: Understanding the rationale behind data selection, including why specific data sources were chosen and any alternative sources considered, helps in assessing the foundation of the application's data.

4. **Data Quality Assessment**: To ensure data reliability, it's crucial to identify who assesses data quality, whether it's an ongoing process, the key aspects evaluated, the review process, and the defined quality criteria.

5. **Required Data Quality**: Determining the level of data quality necessary for the application to meet its objectives and requirements helps align expectations and performance.

6. **Data Quality Thresholds**: This question focuses on whether threshold values have been set for data quality and the reasons for choosing them, along with what actions are taken when data quality falls below or exceeds these thresholds.

7. **Documentation of Data Model Semantic**: This question focuses on whether the meaning and structure of data have been clearly defined in the data model. This includes checking if the team has established the interpretation of data, including any abbreviations or codes used, ensuring consistency and understanding in data usage.

8. **Data Subject to Security Requirements**: This helps identify whether the application handles data subject to security regulations like FTC and the rationale behind using such data.

9. **Data Security Measures**: To protect data, understanding the technical, organizational, and other security measures put in place by the product owner or developer is essential.

These questions assist in comprehensively assessing the data-related aspects of the application, ensuring data quality, security, and compliance with relevant regulations.


### Data Preparation

: In the Data Preparation section, the focus is on the process of getting the data ready for use in the application. Here are concise descriptions of the key questions and their purposes:

1. **Shortcomings in Data Quality**: Identify and document any shortcomings in the quality of input data, including missing values, errors, inaccuracies, outdated information, and inconsistencies.

2. **Modification of Input Datasets**: Understand the steps taken by the product owner, developer, or operator to address data quality issues, including whether modifications are made manually or automatically.

3. **Reporting Data Errors**: Determine if data errors are reported to data suppliers and whether missing entries are replaced or ignored. Documenting data weaknesses for future benchmarking is also important.

4. **Documentation of Data Preparation**: Learn how the data preparation process is documented and tracked during the operation of the application.

5. **Enhancement of Dataset Quality**: Understand how data preparation improves dataset quality and how this impact is measured, including the criteria for benchmarking unprocessed and pre-processed data.

6. **Impact on Application Results**: Assess whether the quality of data preparation affects the operation and results of the application, and how the application responds to differently cleansed data.

7. **Mapping Data Preparation in the Application**: Learn how data preparation has been integrated into the development, testing, validation, and operation processes of the application.

8. **Monitoring Data Preparation Quality**: Understand the quality assurance mechanisms in place for data preparation, including how quality assurance works, when it starts, and how its work is documented.

9. **Addressing Risks**: Identify and address any risks associated with data preparation, as well as any risks related to the application and development environment that data preparation may mitigate.

10. **Data Management Framework**: Learn about the framework conditions and responsibilities governing data management for the application, including applicable frameworks and structures.

11. **Data Management System**: Understand the data management system used, such as SQL databases, NoSQL databases, data warehouses, or flat files, and how data is stored and maintained.

These questions are essential for ensuring that data used by the application is of high quality and that the data preparation process is well-documented and effective in enhancing data quality. They also address risk management and data management structures.


### Modeling

: In the Modeling section, the focus is on the data analysis methods and datasets used for training, validation, and testing in the application. Here are concise descriptions of the key questions and their purposes:

1. **Data Analysis Methods**: Identify the data analysis methods used in the modeling process and the criteria for their selection. These methods can include frequent pattern mining, classification, cluster analysis, and outlier detection.

2. **Training Datasets**: Gather information about the training datasets, including their scope, contents, and quality. Understanding the data used for model training is essential.

3. **Selection or Generation of Training Datasets**: Learn how the training datasets were selected or generated and any tools or programs used in the process. Identify potential errors in the training data.

4. **Updating Training Datasets**: Determine how the training datasets are updated during the system's life cycle, whether the model remains stable or is continuously refined with additional data, and the quality assurance processes in place.

5. **Validation Datasets**: Collect information about the validation datasets, including scope, contents, and quality, to ensure the model's accuracy.

6. **Selection or Generation of Validation Datasets**: Understand how validation datasets were selected or generated and the tools or programs used. Highlight potential errors in validation data.

7. **Updating Validation Datasets**: Explore how validation datasets are updated during the system's life cycle, whether the model remains stable, and the quality assurance of the validation process.

8. **Test Datasets**: Gather details about the test datasets, including scope, contents, and quality. This is essential for verifying model performance.

9. **Selection or Generation of Test Datasets**: Learn about the process of selecting or generating test data and any tools or programs used. Identify potential errors in test data.

10. **Updating Test Datasets**: Understand how test datasets are updated during the system's life cycle, whether the model remains stable, and the quality assurance of the testing process.

11. **Tracking Modeling and Testing**: Collect information on how modeling, model validation, and model testing are documented, ensuring transparency in the process.

12. **Addressing Risks**: Identify how the modeling process addresses any risks detected in the application, including the type of risk analysis conducted for modeling and related factors impacting the modeling process.

These questions help ensure that the modeling process is well-documented, and that the data used for training, validation, and testing is of high quality, aligning with the objectives of the application. Additionally, it addresses the proactive management of risks in the modeling process.


### Evaluation

: In the Evaluation section, the focus is on assessing the performance and effectiveness of the model in the application. Here are concise descriptions of the key questions and their purposes:

1. **Validation Methods and Selection Criteria**: Identify the validation methods used and the criteria for their selection. Understand how the model's quality has been reviewed, how decisions/forecasts have been tracked, and how the impact of individual criteria on decisions has been analyzed. Assess model fairness.

2. **Results of Model Validation and Evaluation**: Gather information on the results of model validation, how they were documented and interpreted, and the traceability of the model's response. Evaluate the extent to which the model is sufficiently accurate and how potentially contradictory statements have been assessed. Consider the empirical data used for interpreting results, who reviewed the validation results, and how these results will be used for future validation exercises.

3. **Benchmarking Model Performance**: Determine whether the model's performance has been benchmarked against alternative methods or models for data analysis. Understand the parameters used for benchmarking and the implications for model evaluation.

4. **Handling Faulty or Manipulated Datasets**: Learn about the application's response to faulty or manipulated datasets at various stages, including training, validation, testing, and operational stages. Understand the results of exposing the model to such data.

5. **Accomplishing Objectives and Intended Purposes**: Assess whether the initial objectives and impacts set by the product owner have been achieved. Understand how this achievement has been measured and whether additional objectives and impacts have been realized.

These questions are essential for evaluating the performance and effectiveness of the model, ensuring that it aligns with its intended purposes and objectives, and addressing potential risks and shortcomings in the modeling process.


### Deployment

: In the Deployment & Monitoring section, the focus is on the deployment and ongoing monitoring of the application, including its integration into the system architecture and processes. Here are concise descriptions of the key questions and their purposes:

1. **Model Update Intervals**: Determine at what intervals the model is updated to reflect current training data and whether the model is static or dynamic.

2. **Application Integration in System Architecture**: Learn how the application is embedded in the surrounding system architecture, including system design, interfaces with other components, and dependencies on these components and their changes.

3. **Application Integration in Process Landscape**: Understand how and when the application is integrated into the product owner's process landscape, considering incidents and framework conditions, and whether the conditions are consistent or vary.

4. **Human-Machine Interaction Features**: Identify the major features of human-machine interaction in the application, including user influence, information communication, and the application's autonomy.

5. **Providing KPIs to Decision-Makers**: Understand how key performance indicators (KPIs) of the application's decisions are provided to decision-makers, including the communication of decision quality or uncertainty.

6. **Application Performance Monitoring**: Learn how and how often the performance of the application is monitored or reviewed during operation.

7. **Intervention Processes for Faulty Performance**: Explore alternative intervention processes in case of faulty or poor system performance, considering dependencies on the application in business processes.

8. **User Qualifications**: Understand the qualifications users of the application need, including their knowledge about the application's impact.

9. **User Overruling of Decisions**: Determine how users can overrule decisions or proposals made by the application, and assess the level of autonomy granted to the application.

10. **Criteria for Application Decisions**: Identify the criteria governing decisions or proposals submitted to the user and distinguish between those that are submitted and those that are not.

11. **Compliance with Laws and Regulations**: Understand the extent to which the application complies with applicable laws and regulations and obtain assessments from various parties involved.

12. **Ethical Concerns**: Explore any ethical concerns related to the use of the application, beyond statutory aspects.

13. **Understanding and Tracking Decisions**: Assess the extent to which users can understand and track the decisions or proposals made by the application.

14. **Understanding How the Application Works**: Determine if users have knowledge about the internal processes underlying the application.

15. **Protection from Misuse**: Identify the steps taken to protect the application from potential misuse.

16. **Exploration of Misuse Types**: Understand what types of misuse possibilities have been analyzed, and whether knowledge is limited to theoretical ideas.

17. **Exploration of Attacks**: Learn if types of attacks on the application and embedded processes have been explored and addressed during the planning stage.

18. **Residual Risks**: Understand the residual risks that still persist and require attention, and specify criteria for assessing their tolerability.

19. **Factors Impacting Reliability (System)**: Explore factors that impact the reliability of the overall system in which the application is embedded, and how these factors affect the application.

20. **Factors Impacting Reliability (Decisions/Proposals)**: Understand additional variables that may impact the reliability of the application's decisions, beyond the application's framework conditions.

21. **Avoiding Unequal Treatment**: Determine the extent to which any unequal treatment of individuals, facts, or matters arising from using the application can be ruled out and how incidents are verified.

22. **Sustainability Considerations**: Explore whether sustainability considerations, such as energy efficiency, have been taken into account in operating the AI components.

These questions are essential for ensuring the successful deployment and ongoing monitoring of the application, addressing issues related to ethics, compliance, misuse, and reliability, and considering sustainability aspects.


### Misc

: In this section, various miscellaneous topics related to the AI project are addressed. Each topic provides insights into different aspects of the project's management and development:

1. **Demand and Change Management**: Understand how demand and change management for developing the application/system have been designed, including the tools used, and the involvement of the product owner in managing changes and requirements.

2. **Software Development**: Learn how software development is structured, including the tools, libraries, and methodologies used in the development process.

3. **Quality Assurance**: Understand the structure of quality assurance, including the testing and acceptance processes, as well as how developer tests are designed to ensure the quality of the application.

4. **Project Management**: Gain insights into the structure of project management, including the approaches and methods chosen for managing the AI project.

5. **Rollout**: Understand how the application/system rollout is structured, whether it involves pilot users, a gradual rollout, or a big-bang approach, and what framework conditions are in place or still needed.

6. **Acceptance Management**: Learn how staff, clients, and other stakeholders have been prepared for the application/system rollout and how their understanding and readiness for change have been promoted.

7. **Incident Management**: Understand the procedures in place for users and operational units to report malfunctions and incidents to ensure prompt resolution.

8. **Change Management (Staff, Organization)**: Understand the changes in practices, procedures, human resources, and financial management associated with the rollout and how the organization and its staff have been prepared to adapt to these changes.

These miscellaneous topics cover important aspects of the AI project's management, development, quality assurance, and change management, ensuring a comprehensive understanding of the project's structure and processes.


## Audit UI

The recommended way to interact with `AuditCards` is through the UI.

### Find your model

Navigate to the model tab and find your specific model and version.

<p align="left">
  <img src="../../images/model-ui.png" width="703" height="536"/>
</p>

### Click the Audit link and fill out the audit form

You can also upload and existing audit csv, download the current audit as a csv, and add comments via the comment button.

<p align="left">
  <img src="../../images/audit-ui.png" width="716" height="427"/>
</p>