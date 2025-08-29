# Technical Specifications

This directory contains various technical specifications for OpsML. It is an ongoing effort to document the architecture, design decisions, changes, and other important aspects of the project. It is **NOT** feature complete and is subject to change as the project evolves.

**Note**: Specifications are written in markdown format and should be easy to read and understand. And while they are recommended for big changes, they are not mandatory.

## Writing Specifications

When writing specifications, please follow these guidelines for structure:

```markdown
# Title

## Overview
Simple and concise overview of the specification, including its purpose and scope.

## Key Changes: A brief overview of the specification, including its purpose and scope.

## Implementation Details
- Detailed description of the implementation, including code snippets and examples.
- Explanation of any design decisions, trade-offs, and alternatives considered.
- This part is more flexible and is up to the author to decide how to structure it as long as it is clear and easy to understand.


---
*Version: 1.0*  
*Last Updated: [date- YYY-MM-DD]*  
*Author: [Your name]*
```

## Naming Conventions

### Feature-based Specifications
- Feature-based specifications should be named after the feature they are describing. For example, if you are writing a specification for a new feature called "FeatureX", the file name should be `ts-feature-feature_x.md`. This will help in organizing and locating specifications easily.
- Format: `ts-feature-feature_name.md`

### Component-based Specifications
- Component-based specifications should be named after the component they are describing. For example, if you are writing a specification for a component called "ComponentY", the file name should be `ts-component-component_y.md`. This will help in organizing and locating specifications easily.
- Format: `ts-component-component_name.md`


### Issue-based Specifications
- Issue-based specifications should be named after the issue they are describing. For example, if you are writing a specification for an issue number 1234, the file name should be `ts-issue-1234.md`. This will help in organizing and locating specifications easily.
- Format: `ts-issue-number.md`