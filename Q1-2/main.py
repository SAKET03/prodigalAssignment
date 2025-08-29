import json
import re
import time
import zipfile
from typing import List

import pandas as pd
from dotenv import load_dotenv
from groq import RateLimitError
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()


# ==== Models ====
class ProfanityAnalysis(BaseModel):
    agent_has_profanity: bool = Field(description="True if agent used profane language")
    customer_has_profanity: bool = Field(
        description="True if customer used profane language"
    )
    agent_profanity_usage: List[str] = Field(
        description="Specific profane words/phrases used by agent"
    )
    customer_profanity_usage: List[str] = Field(
        description="Specific profane words/phrases used by customer"
    )


class PrivacyAnalysis(BaseModel):
    agent_violated_privacy: bool = Field(
        description="True if agent shared sensitive info without verification"
    )
    sensitive_info_shared: List[str] = Field(
        description="Specific sensitive information shared"
    )
    verification_attempted: bool = Field(
        description="True if agent attempted identity verification"
    )
    verification_methods: List[str] = Field(
        description="Methods used for verification (DOB, address, SSN)"
    )


# ==== LLM ====
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
)


# ==== Helpers ====
def clean_conversation(conversation):
    speaker_text, customer_text = "", ""
    for i in conversation:
        if i["speaker"] == "Agent":
            speaker_text += f"{i['text']}\n"
        elif i["speaker"] == "Customer":
            customer_text += f"{i['text']}\n"
    return f"Agent:\n{speaker_text}\nCustomer:\n{customer_text}"


def load_conversations_from_zip(zip_file):
    """Load and parse JSON conversation files from a zip archive."""
    conversations = {}
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith(".json"):
                    call_id = file_name.replace(".json", "").split("/")[-1]
                    try:
                        with zip_ref.open(file_name) as json_file:
                            content = json_file.read().decode("utf-8")
                            conversation_data = json.loads(content)
                            conversations[call_id] = conversation_data
                    except json.JSONDecodeError:
                        conversations[call_id] = {"error": f"Invalid JSON: {file_name}"}
    except Exception as e:
        print(f"Error processing zip file: {e}")
    return conversations


# ============================================================
# Pattern Matcher
# ============================================================
class PatternMatcher:
    """Optimized pattern matching for profanity and privacy violations"""

    def __init__(self):
        # Profanity patterns
        self.profanity_patterns = [
            r"\bhell\b",
            r"\bdamn\b",
            r"\bcrap\b",
            r"\bf\*+\b",
            r"\bf\*\*\*\b",
            r"\bbullshit\b",
            r"\bf[*\-_]+k\b",
            r"\bass\b",
            r"\bshit\b",
            r"\bdumbass\b",
            r"\bjerk\b",
            r"\bidiot\b",
            r"\bstupid\b",
            r"\bfuck\b",
            r"\bbitch\b",
            r"\bastard\b",
            r"\bprick\b",
        ]

        # Sensitive info patterns
        self.sensitive_info_patterns = [
            r"\$\d+(?:,\d{3})*(?:\.\d{2})?",  # Dollar amounts
            r"\bbalance.*\$?\d+",  # Balance mentions
            r"\bowe.*\$?\d+",  # Debt amounts
            r"\baccount.*\d{4,}",  # Account numbers
            r"\bssn?\s*:?\s*\d{3}-?\d{2}-?\d{4}",  # SSN
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN format
        ]

        # Verification patterns
        self.verification_patterns = [
            r"\bdate\s+of\s+birth\b",
            r"\bdob\b",
            r"\bbirthdate\b",
            r"\baddress\b",
            r"\bstreet\b",
            r"\bcity\b",
            r"\bzip\b",
            r"\bssn\b",
            r"\bsocial\s+security\b",
            r"\blast\s+four\b",
        ]

        # Compile for efficiency
        self.compiled_profanity = [
            re.compile(p, re.IGNORECASE) for p in self.profanity_patterns
        ]
        self.compiled_sensitive = [
            re.compile(p, re.IGNORECASE) for p in self.sensitive_info_patterns
        ]
        self.compiled_verification = [
            re.compile(p, re.IGNORECASE) for p in self.verification_patterns
        ]

    # -----------------------------
    # Profanity Detection
    # -----------------------------
    def detect_profanity(self, conversation):
        agent_profanity, customer_profanity = [], []

        for utt in conversation:
            text = utt.get("text", "")
            speaker = utt.get("speaker", "").lower()

            found = []
            for pattern in self.compiled_profanity:
                found.extend(pattern.findall(text))

            if found:
                if "agent" in speaker:
                    agent_profanity.extend(found)
                elif "customer" in speaker:
                    customer_profanity.extend(found)

        return {
            "agent_has_profanity": len(agent_profanity) > 0,
            "customer_has_profanity": len(customer_profanity) > 0,
            "agent_profanity_usage": list(set(agent_profanity)),
            "customer_profanity_usage": list(set(customer_profanity)),
        }

    # -----------------------------
    # Privacy Detection
    # -----------------------------
    def detect_privacy_violation(self, conversation):
        sensitive_info_shared = []
        verification_attempted = False
        verification_methods = []
        agent_shared_sensitive = False

        for utt in conversation:
            text = utt.get("text", "")
            speaker = utt.get("speaker", "").lower()

            if "agent" in speaker:
                # Sensitive info
                for pattern in self.compiled_sensitive:
                    matches = pattern.findall(text)
                    if matches:
                        sensitive_info_shared.extend(matches)
                        agent_shared_sensitive = True

                # Verification
                for pattern in self.compiled_verification:
                    if pattern.search(text):
                        verification_attempted = True
                        verification_methods.append(pattern.pattern)

        violation = agent_shared_sensitive and not verification_attempted

        return {
            "agent_violated_privacy": violation,
            "sensitive_info_shared": list(set(sensitive_info_shared)),
            "verification_attempted": verification_attempted,
            "verification_methods": list(set(verification_methods)),
        }


# ============================================================
# Pattern Matching Entry Points
# ============================================================
def profanity_detection_pattern(zip_file):
    conversations = load_conversations_from_zip(zip_file)
    matcher = PatternMatcher()
    agent_profanity, customer_profanity = {}, {}

    for conv_id, conversation in conversations.items():
        result = matcher.detect_profanity(conversation)
        if result["agent_has_profanity"]:
            agent_profanity[conv_id] = result["agent_profanity_usage"]
        if result["customer_has_profanity"]:
            customer_profanity[conv_id] = result["customer_profanity_usage"]

    agent_df = pd.DataFrame(
        [(k, v) for k, v in agent_profanity.items()],
        columns=["id", "usage"],
    )
    customer_df = pd.DataFrame(
        [(k, v) for k, v in customer_profanity.items()],
        columns=["id", "usage"],
    )
    return agent_df, customer_df


def privacy_detection_pattern(zip_file):
    conversations = load_conversations_from_zip(zip_file)
    matcher = PatternMatcher()
    violations = {}

    for conv_id, conversation in conversations.items():
        result = matcher.detect_privacy_violation(conversation)
        if result["agent_violated_privacy"]:
            violations[conv_id] = result["sensitive_info_shared"]

    return pd.DataFrame(
        [(k, v) for k, v in violations.items()],
        columns=["id", "sensitive_info"],
    )


# ==== Prompt Fillers ====
def privacy_fill_prompt(conversation_to_analyze):
    return f"""
        Analyze this debt collection conversation for privacy compliance violations.

        Conversation:
        {conversation_to_analyze}

        Instructions:
        - Did the agent share sensitive information (account balance, payment amounts, account details) WITHOUT proper identity verification?
        - Look for verification attempts: asking for DOB, address, SSN, security questions
        - Identify what sensitive information was shared
        - Determine if verification occurred BEFORE sharing sensitive data

        Respond with JSON:
        {{
            "agent_violated_privacy": boolean,
            "sensitive_info_shared": [list],
            "verification_attempted": boolean,
            "verification_methods": [list]
        }}
    """


def profanity_fill_prompt(conversation_to_analyze):
    return f"""
        Analyze this debt collection conversation for profanity usage.

        Conversation:
        {conversation_to_analyze}

        Instructions:
        - Identify profanity by Agent and Customer (mild or strong)
        - Include censored profanity (f***, s***)
        - Provide exact words/phrases

        Respond with JSON:
        {{
            "agent_has_profanity": boolean,
            "customer_has_profanity": boolean,
            "agent_profanity_usage": [list],
            "customer_profanity_usage": [list]
        }}
    """


# ==== Detection Functions ====
def privacy_detection_llm(zip_file):
    batch_input, privacy_violated = [], {}
    structured_llm = llm.with_structured_output(PrivacyAnalysis)
    conversations = load_conversations_from_zip(zip_file)
    conversation_ids = list(conversations.keys())

    for i in conversation_ids:
        cleaned = clean_conversation(conversations[i])
        batch_input.append(privacy_fill_prompt(cleaned))

    outputs, batch_size, i = [], 5, 0
    while i < len(batch_input):
        try:
            result = structured_llm.batch(batch_input[i : i + batch_size])
            outputs.extend(result)
            i += batch_size
        except RateLimitError:
            time.sleep(60)
        except Exception:
            i += batch_size

    for idx, output in enumerate(outputs):
        conv_id = conversation_ids[idx]
        if output.agent_violated_privacy and not output.verification_attempted:
            privacy_violated[conv_id] = output.sensitive_info_shared

    return pd.DataFrame(
        [(k, v) for k, v in privacy_violated.items()],
        columns=["id", "sensitive_info"],
    )


def profanity_detection_llm(zip_file):
    batch_input, agent_profanity, customer_profanity = [], {}, {}
    structured_llm = llm.with_structured_output(ProfanityAnalysis)
    conversations = load_conversations_from_zip(zip_file)
    conversation_ids = list(conversations.keys())

    for i in conversation_ids:
        cleaned = clean_conversation(conversations[i])
        batch_input.append(profanity_fill_prompt(cleaned))

    outputs, batch_size, i = [], 5, 0
    while i < len(batch_input):
        try:
            result = structured_llm.batch(batch_input[i : i + batch_size])
            outputs.extend(result)
            i += batch_size
        except RateLimitError:
            time.sleep(60)
        except Exception:
            i += batch_size

    for idx, output in enumerate(outputs):
        conv_id = conversation_ids[idx]
        if output.agent_has_profanity:
            agent_profanity[conv_id] = output.agent_profanity_usage
        if output.customer_has_profanity:
            customer_profanity[conv_id] = output.customer_profanity_usage

    agent_df = pd.DataFrame(
        [(k, v) for k, v in agent_profanity.items()],
        columns=["id", "usage"],
    )
    customer_df = pd.DataFrame(
        [(k, v) for k, v in customer_profanity.items()],
        columns=["id", "usage"],
    )
    return agent_df, customer_df
