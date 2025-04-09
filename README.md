# Synthetic Virtual Conversation Files (vCon)

This repository contains synthetic virtual conversation files (vCon) created using the [vcon_faker](https://github.com/vcon-dev/vcon_faker) tool. These files simulate interactions between a customer service agent and a customer across various business scenarios. The conversations are generated based on predefined prompts and include metadata such as agent and customer names, business type, and emotional context.

## About vcon_faker

The vcon_faker tool is a powerful Python-based utility that generates realistic synthetic conversations for testing and development purposes. It leverages AI models to create natural-sounding dialogues between agents and customers, complete with appropriate metadata and context.

## Structure of a vCon (Virtual Conversation)

A vCon (Virtual Conversation) is a standardized JSON-based container designed to store and exchange data about real-time human conversations. It can encapsulate information from various communication modes, such as phone calls, video conferences, SMS, MMS, emails, and more. A vCon organizes this data into structured components for use in applications, data analysis, and regulatory compliance.

### Key Components of a vCon

A vCon contains five main sections:

1. **Metadata**: Provides details about the conversation's context, including unique identifiers, timestamps, subject, and references to previous versions of the vCon.
2. **Parties**: Captures details about the participants in the conversation, including their roles, identifiers, and contact information.
3. **Dialog**: Stores the actual content of the conversation (e.g., text, audio, or video).
4. **Analysis**: Includes derived data such as transcripts, translations, sentiment analysis, or semantic tagging.
5. **Attachments**: Stores additional files related to the conversation, such as slides, images, or documents.

### Structure of a vCon JSON Object

A vCon JSON object can be in one of three forms:
- **Unsigned**: Initial or intermediate state during data collection
- **Signed**: Verified state with a digital signature for immutability
- **Encrypted**: Secure state to protect sensitive data

#### General Structure
```json
{
  "vcon": "0.0.1",           // Syntax version
  "uuid": "string",          // Unique identifier
  "created_at": "date",      // Creation timestamp
  "updated_at": "date",      // Last modified timestamp
  "subject": "string",       // Optional topic of the conversation
  "redacted": {},            // Reference to the unredacted version (if applicable)
  "appended": {},            // Reference to additional information (if applicable)
  "group": [],               // Aggregation of multiple vCons
  "parties": [],             // Array of participant details
  "dialog": [],              // Array of conversation segments
  "analysis": [],            // Array of analysis data
  "attachments": []          // Array of attachment data
}
```

#### Parties
Each participant in the conversation is represented as an object:
```json
{
  "tel": "string",          // Telephone number
  "mailto": "string",       // Email address
  "name": "string",         // Participant's name
  "role": "string",         // Role in the conversation (e.g., agent, customer)
  "uuid": "string"          // Unique identifier for the participant
}
```

#### Dialog
Each segment of the conversation is captured as a dialog object:
```json
{
  "type": "string",         // Type (e.g., recording, text)
  "start": "date",          // Start timestamp
  "duration": "number",     // Duration in seconds
  "parties": [],            // Array of participant indices
  "mimetype": "string",     // MIME type of the content
  "filename": "string",     // Original filename (if applicable)
  "body": "string",         // Content (base64-encoded if inline)
  "encoding": "string"      // Encoding type (e.g., base64url)
}
```

#### Analysis
Derived insights about the conversation are stored in analysis objects:
```json
{
  "type": "string",         // Analysis type (e.g., transcript, sentiment)
  "dialog": [],             // Array of dialog indices related to the analysis
  "mimetype": "string",     // MIME type of the analysis file
  "filename": "string",     // Original filename
  "vendor": "string",       // Vendor or product name
  "body": "string",         // Content (base64-encoded if inline)
  "encoding": "string"      // Encoding type (e.g., base64url)
}
```

#### Attachments
Attachments provide supplemental data:
```json
{
  "type": "string",         // Type or purpose of the attachment
  "start": "date",          // Timestamp when the attachment was exchanged
  "party": "number",        // Index of the contributing participant
  "mimetype": "string",     // MIME type of the attachment
  "filename": "string",     // Original filename
  "body": "string",         // Content (base64-encoded if inline)
  "encoding": "string"      // Encoding type (e.g., base64url)
}
```

### Security and Integrity

- **Signing**: vCons can be signed using JWS (JSON Web Signature) to ensure their integrity and authenticity.
- **Encryption**: Sensitive vCons can be encrypted using JWE (JSON Web Encryption) to protect their content.
- **Versioning**: Redacted and appended vCons reference their original versions to maintain a history of changes.

### Example Use Cases

- **Customer Support**: Storing call recordings, transcripts, and attachments for quality assurance and analytics.
- **Legal Compliance**: Maintaining immutable records of conversations with signatures for regulatory purposes.
- **Machine Learning**: Using vCon data as input for training AI models while adhering to data privacy laws.

## Example Conversation Format

The conversations are formatted as an array of message objects, each containing:
- `speaker`: Denotes whether the speaker is the Agent or Customer.
- `message`: The content of the message spoken by the speaker.

Example:
```json
{
  "conversation": [
    {"speaker": "Agent", "message": "Hello! My name is John Doe from Car Rentals. How can I assist you today?"},
    {"speaker": "Customer", "message": "Hi, I need to inquire about my recent rental."},
    {"speaker": "Agent", "message": "Certainly! Could I have your booking reference number, please?"}
  ]
}
```

## Usage

These synthetic vCon files can be used for various testing and demo scenarios such as:
- Training customer service agents
- Demonstrating the capabilities of customer interaction models
- Testing conversational AI systems
- Development and testing of vCon processing applications
- Creating realistic test datasets for machine learning models

## Getting Started with vcon_faker

To generate your own synthetic conversations using vcon_faker:

1. Clone the vcon_faker repository:
   ```bash
   git clone https://github.com/vcon-dev/vcon_faker.git
   ```

2. Follow the installation and setup instructions in the [vcon_faker documentation](https://github.com/vcon-dev/vcon_faker#readme)

3. Use the tool to generate synthetic conversations with your desired parameters and scenarios

## Contribution

Contributions to this repository are welcome. If you have any suggestions or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```