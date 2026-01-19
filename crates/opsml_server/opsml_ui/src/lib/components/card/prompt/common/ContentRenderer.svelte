<script lang="ts">
  import { Provider } from '$lib/components/genai/types';
  import type { MessageNum } from '$lib/components/genai/provider/types';
  import type { ChatMessage } from '$lib/components/genai/provider/openai/v1/chat/request';
  import type { MessageParam, TextBlockParam } from '$lib/components/genai/provider/anthropic/v1/request';
  import type { GeminiContent } from '$lib/components/genai/provider/google/v1/generate/request';
  
  // Icons
  import { FileText, Image as ImageIcon, AudioWaveform, Wrench, Terminal, Code2 } from 'lucide-svelte';

  // Specific imports for strict type checking
  import { 
    OPENAI_CONTENT_PART_TEXT, 
    OPENAI_CONTENT_PART_IMAGE_URL,
    OPENAI_CONTENT_PART_INPUT_AUDIO,
    OPENAI_CONTENT_PART_FILE
  } from '$lib/components/genai/provider/openai/v1/chat/request';

  import { 
    TEXT_TYPE as ANTHROPIC_TEXT, 
    IMAGE_TYPE as ANTHROPIC_IMAGE,
    TOOL_USE_TYPE as ANTHROPIC_TOOL
  } from '$lib/components/genai/provider/anthropic/v1/request';

  let { message, provider } = $props<{ 
    message: MessageNum; 
    provider: Provider 
  }>();

  // Strict Type Guards -----------------------------------------

  function asOpenAI(m: MessageNum): ChatMessage {
    return m as ChatMessage;
  }

  function asAnthropic(m: MessageNum): MessageParam {
    return m as MessageParam;
  }
  
  function asAnthropicSystem(m: MessageNum): TextBlockParam {
    return m as TextBlockParam;
  }

  function asGemini(m: MessageNum): GeminiContent {
    return m as GeminiContent;
  }
</script>

<div class="flex flex-col gap-3 w-full">
  
  {#if provider === Provider.OpenAI}
    {@const openaiMsg = asOpenAI(message)}
    {#each openaiMsg.content as part}
      
      {#if part.type === OPENAI_CONTENT_PART_TEXT}
        <div class="whitespace-pre-wrap text-sm text-primary-950 font-medium font-mono leading-relaxed">
          {part.text}
        </div>
      
      {:else if part.type === OPENAI_CONTENT_PART_IMAGE_URL}
        <div class="group relative rounded-xl border-2 border-black overflow-hidden my-2 max-w-sm shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] bg-surface-50">
          <div class="absolute top-2 left-2 bg-white/90 backdrop-blur border border-black px-2 py-1 rounded-md text-[10px] font-bold uppercase flex items-center gap-1 z-10">
            <ImageIcon class="w-3 h-3 text-purple-600"/>
            Image
          </div>
          <img src={part.image_url.url} alt="User upload" class="w-full h-auto" />
        </div>

      {:else if part.type === OPENAI_CONTENT_PART_FILE}
        <div class="flex items-center gap-3 bg-white border-2 border-black p-3 rounded-xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] max-w-md my-1">
          <div class="bg-blue-100 border-2 border-black p-2 rounded-lg">
            <FileText class="w-5 h-5 text-blue-700" />
          </div>
          <div class="flex flex-col overflow-hidden">
            <span class="text-xs font-black uppercase text-slate-500 tracking-wider">Uploaded File</span>
            <span class="font-mono text-sm font-bold text-slate-900 truncate">{part.file.filename || 'Unknown File'}</span>
          </div>
        </div>
      
      {:else if part.type === OPENAI_CONTENT_PART_INPUT_AUDIO}
        <div class="flex items-center gap-3 bg-white border-2 border-black p-3 rounded-xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] max-w-md my-1">
          <div class="bg-pink-100 border-2 border-black p-2 rounded-lg">
             <AudioWaveform class="w-5 h-5 text-pink-700" />
          </div>
          <div class="flex flex-col">
            <span class="text-xs font-black uppercase text-slate-500 tracking-wider">Input Audio</span>
            <span class="font-mono text-sm font-bold text-slate-900 uppercase">{part.input_audio.format} Format</span>
          </div>
        </div>
      {/if}

    {/each}

  {:else if provider === Provider.Anthropic}
    {#if 'content' in message}
      {@const anthropicMsg = asAnthropic(message)}
      {#each anthropicMsg.content as block}
        
        {#if block.type === ANTHROPIC_TEXT}
          <div class="whitespace-pre-wrap text-sm text-primary-950 font-medium font-mono leading-relaxed">
            {block.text}
          </div>
        
        {:else if block.type === ANTHROPIC_IMAGE}
          {@const src = block.source.type === 'base64' 
            ? `data:${block.source.media_type};base64,${block.source.data}`
            : block.source.url}
          <div class="group relative rounded-xl border-2 border-black overflow-hidden my-2 max-w-sm shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] bg-surface-50">
             <div class="absolute top-2 left-2 bg-white/90 backdrop-blur border border-black px-2 py-1 rounded-md text-[10px] font-bold uppercase flex items-center gap-1 z-10">
              <ImageIcon class="w-3 h-3 text-purple-600"/>
              Image
            </div>
            <img {src} alt="Anthropic upload" class="w-full h-auto" />
          </div>

        {:else if block.type === ANTHROPIC_TOOL}
          <div class="bg-surface-50 border-2 border-black rounded-xl overflow-hidden shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] my-2 max-w-2xl">
            <div class="px-3 py-2 border-b-2 border-black bg-white flex items-center justify-between">
              <div class="flex items-center gap-2">
                <Wrench class="w-4 h-4 text-purple-600" />
                <span class="font-bold text-xs uppercase tracking-wider text-slate-900">Tool Call: {block.name}</span>
              </div>
              <Code2 class="w-3 h-3 text-slate-400" />
            </div>
            <div class="p-3 bg-slate-50 overflow-x-auto">
              <pre class="text-xs font-mono text-slate-800">{JSON.stringify(block.input, null, 2)}</pre>
            </div>
          </div>
        {/if}
      {/each}
    
    {:else if 'text' in message && 'type' in message}
      {@const sysMsg = asAnthropicSystem(message)}
      <div class="flex gap-3 bg-surface-100 border-2 border-black border-dashed p-3 rounded-xl items-start opacity-75">
        <Terminal class="w-4 h-4 mt-0.5 text-slate-600 shrink-0" />
        <div class="whitespace-pre-wrap text-sm text-slate-700 font-medium font-mono leading-relaxed">
          {sysMsg.text}
        </div>
      </div>
    {/if}

  {:else if (provider === Provider.Gemini || provider === Provider.Google || provider === Provider.Vertex)}
    {@const geminiMsg = asGemini(message)}
    {#each geminiMsg.parts as part}
      
      {#if 'text' in part}
        <div class="whitespace-pre-wrap text-sm text-primary-950 font-medium font-mono leading-relaxed">
          {part.text}
        </div>
      
      {:else if 'inlineData' in part}
        <div class="group relative rounded-xl border-2 border-black overflow-hidden my-2 max-w-sm shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] bg-surface-50">
           <div class="absolute top-2 left-2 bg-white/90 backdrop-blur border border-black px-2 py-1 rounded-md text-[10px] font-bold uppercase flex items-center gap-1 z-10">
              <ImageIcon class="w-3 h-3 text-purple-600"/>
              Image
            </div>
          <img 
            src={`data:${part.inlineData.mimeType};base64,${part.inlineData.data}`} 
            alt="Gemini upload" 
            class="w-full h-auto" 
          />
        </div>
      
      {:else if 'functionCall' in part}
         <div class="bg-surface-50 border-2 border-black rounded-xl overflow-hidden shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] my-2 max-w-2xl">
            <div class="px-3 py-2 border-b-2 border-black bg-white flex items-center justify-between">
              <div class="flex items-center gap-2">
                <Wrench class="w-4 h-4 text-blue-600" />
                <span class="font-bold text-xs uppercase tracking-wider text-slate-900">Function: {part.functionCall.name}</span>
              </div>
              <Code2 class="w-3 h-3 text-slate-400" />
            </div>
            <div class="p-3 bg-slate-50 overflow-x-auto">
              <pre class="text-xs font-mono text-slate-800">{JSON.stringify(part.functionCall.args, null, 2)}</pre>
            </div>
          </div>
      {/if}

    {/each}
  {/if}
</div>