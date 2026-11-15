# Integrations

The bundled integration documents live in `../integrations/`, relative to this
index. Follow the local links below when inspecting an integration.

## Required selection rule

1. Choose the cloud destination and read [cloud-instrumentation.md](cloud-instrumentation.md).
2. Inspect the framework's native OTel support and the application's existing provider.
3. Read the matching bundled page's cloud guidance. Prefer supported native OTel,
   then a verified OTel instrumentor, then manual spans for actual operations.
4. Apply content controls and use the selected exporter through `deepeval-otel`.
5. Use the retained DeepEval examples only for explicitly requested local evals;
   follow [local-evaluations.md](local-evaluations.md) and skip hosted-service setup.

Model documents configure evaluation-model access; they do not select the tracing
backend. Vector-store pages provide retrieval context; their native DeepEval
wrappers do not automatically feed cloud exporters. A framework's use of OTel does
not prove that its DeepEval adapter avoids installing a hosted-service processor.

## Framework Docs

- [Vercel AI SDK](../integrations/frameworks/ai-sdk.mdx)
- [Mastra](../integrations/frameworks/mastra.mdx)
- [LangGraph](../integrations/frameworks/langgraph.mdx)
- [LangChain](../integrations/frameworks/langchain.mdx)
- [OpenAI Agents](../integrations/frameworks/openai-agents.mdx)
- [LlamaIndex](../integrations/frameworks/llamaindex.mdx)
- [Pydantic AI](../integrations/frameworks/pydanticai.mdx)
- [CrewAI](../integrations/frameworks/crewai.mdx)
- [Google ADK](../integrations/frameworks/google-adk.mdx)
- [Strands](../integrations/frameworks/strands.mdx)
- [AgentCore](../integrations/frameworks/agentcore.mdx)
- [OpenAI SDK](../integrations/frameworks/openai.mdx)
- [Anthropic SDK](../integrations/frameworks/anthropic.mdx)
- [Hugging Face](../integrations/frameworks/huggingface.mdx)

## Model Docs

- [Vercel AI SDK](../integrations/models/ai-sdk.mdx)
- [TypeSafe AI](../integrations/models/typesafe-ai.mdx)
- [OpenAI](../integrations/models/openai.mdx)
- [Azure OpenAI](../integrations/models/azure-openai.mdx)
- [Anthropic](../integrations/models/anthropic.mdx)
- [Gemini](../integrations/models/gemini.mdx)
- [Amazon Bedrock](../integrations/models/amazon-bedrock.mdx)
- [Vertex AI](../integrations/models/vertex-ai.mdx)
- [Grok](../integrations/models/grok.mdx)
- [OpenRouter](../integrations/models/openrouter.mdx)
- [LiteLLM](../integrations/models/litellm.mdx)
- [Ollama](../integrations/models/ollama.mdx)
- [vLLM](../integrations/models/vllm.mdx)
- [LM Studio](../integrations/models/lmstudio.mdx)
- [Portkey](../integrations/models/portkey.mdx)
- [DeepSeek](../integrations/models/deepseek.mdx)
- [Moonshot](../integrations/models/moonshot.mdx)

## Vector Database Docs

- [Chroma](../integrations/vector-databases/chroma.mdx)
- [Elasticsearch](../integrations/vector-databases/elasticsearch.mdx)
- [PGVector](../integrations/vector-databases/pgvector.mdx)
- [Qdrant](../integrations/vector-databases/qdrant.mdx)
- [Weaviate](../integrations/vector-databases/weaviate.mdx)
- [Cognee](../integrations/vector-databases/cognee.mdx)

## Shared exporter setup

Use [deepeval-otel](../../deepeval-otel/SKILL.md) for Azure Monitor, Foundry,
or AWS X-Ray routing. Keep one provider lifecycle. Native DeepEval `@observe`
is reserved for optional local evaluation instrumentation; cloud spans are emitted
by OTel instrumentation and the [manual helper](../templates/cloud_spans.py).
