import { c as create_ssr_component, v as validate_component, d as add_attribute, e as escape, f as each } from "../../../chunks/ssr.js";
import { C as Card, B as Button, P as Phone } from "../../../chunks/Card.js";
import { I as Icon } from "../../../chunks/Icon.js";
import { S as Scale } from "../../../chunks/scale.js";
const Arrow_left = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  const iconNode = [["path", { "d": "m12 19-7-7 7-7" }], ["path", { "d": "M19 12H5" }]];
  return `${validate_component(Icon, "Icon").$$render($$result, Object.assign({}, { name: "arrow-left" }, $$props, { iconNode }), {}, {
    default: () => {
      return `${slots.default ? slots.default({}) : ``}`;
    }
  })}`;
});
const Send = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  const iconNode = [
    [
      "path",
      {
        "d": "M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"
      }
    ],
    ["path", { "d": "m21.854 2.147-10.94 10.939" }]
  ];
  return `${validate_component(Icon, "Icon").$$render($$result, Object.assign({}, { name: "send" }, $$props, { iconNode }), {}, {
    default: () => {
      return `${slots.default ? slots.default({}) : ``}`;
    }
  })}`;
});
const User = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  const iconNode = [
    [
      "path",
      {
        "d": "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"
      }
    ],
    ["circle", { "cx": "12", "cy": "7", "r": "4" }]
  ];
  return `${validate_component(Icon, "Icon").$$render($$result, Object.assign({}, { name: "user" }, $$props, { iconNode }), {}, {
    default: () => {
      return `${slots.default ? slots.default({}) : ``}`;
    }
  })}`;
});
function formatTime(date) {
  return date.toLocaleTimeString("en-ZA", { hour: "2-digit", minute: "2-digit" });
}
const ChatMessage = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { message } = $$props;
  if ($$props.message === void 0 && $$bindings.message && message !== void 0) $$bindings.message(message);
  return `<div class="${"flex " + escape(
    message.type === "user" ? "justify-end" : "justify-start",
    true
  ) + " mb-4"}"><div class="${"flex max-w-sm space-x-2 " + escape(
    message.type === "user" ? "flex-row-reverse space-x-reverse" : "",
    true
  )}"> <div class="flex-shrink-0"><div class="${"w-8 h-8 rounded-full flex items-center justify-center " + escape(
    message.type === "user" ? "bg-legal-primary" : "bg-legal-accent",
    true
  )}">${message.type === "user" ? `${validate_component(User, "User").$$render($$result, { class: "h-4 w-4 text-white" }, {}, {})}` : `${validate_component(Scale, "Scale").$$render($$result, { class: "h-4 w-4 text-white" }, {}, {})}`}</div></div>  <div class="${"flex flex-col " + escape(message.type === "user" ? "items-end" : "items-start", true)}"><div${add_attribute(
    "class",
    message.type === "user" ? "chat-bubble-user" : "chat-bubble-assistant",
    0
  )}><p class="text-sm whitespace-pre-wrap">${escape(message.content)}</p></div> <span class="text-xs text-legal-gray-400 mt-1">${escape(formatTime(message.timestamp))}</span></div></div></div>`;
});
const ChatWidget = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { isEmbedded = false } = $$props;
  let messages = [];
  let currentMessage = "";
  let isLoading = false;
  if ($$props.isEmbedded === void 0 && $$bindings.isEmbedded && isEmbedded !== void 0) $$bindings.isEmbedded(isEmbedded);
  return `${validate_component(Card, "Card").$$render($$result, { class: isEmbedded ? "h-96" : "h-128" }, {}, {
    default: () => {
      return ` <div class="flex items-center justify-between p-4 border-b border-legal-gray-200"><div class="flex items-center space-x-3" data-svelte-h="svelte-1pcn2ba"><div class="w-8 h-8 bg-legal-primary rounded-full flex items-center justify-center"><span class="text-white font-semibold text-sm">V</span></div> <div><h3 class="font-semibold text-legal-gray-900">Legal Assistant</h3> <p class="text-xs text-legal-gray-500">Professional legal guidance</p></div></div> ${validate_component(Button, "Button").$$render(
        $$result,
        {
          variant: "accent",
          size: "sm",
          class: "flex items-center space-x-1"
        },
        {},
        {
          default: () => {
            return `${validate_component(Phone, "Phone").$$render($$result, { class: "h-3 w-3" }, {}, {})} <span class="text-xs" data-svelte-h="svelte-cko9bi">Call</span>`;
          }
        }
      )}</div>  <div class="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">${messages.length === 0 ? `<div class="text-center text-legal-gray-500 py-8" data-svelte-h="svelte-1cqd2ya"><p class="mb-2">Welcome to Verdict360 Legal Assistant</p> <p class="text-sm">Ask me any South African legal question</p></div>` : ``} ${each(messages, (message) => {
        return `${validate_component(ChatMessage, "ChatMessage").$$render($$result, { message }, {}, {})}`;
      })} ${``}</div>  <div class="p-4 border-t border-legal-gray-200"><div class="flex space-x-2"><textarea placeholder="Ask your legal question..." rows="2" class="flex-1 resize-none textarea-legal text-sm" ${""}>${escape("")}</textarea> ${validate_component(Button, "Button").$$render(
        $$result,
        {
          variant: "primary",
          size: "md",
          disabled: !currentMessage.trim() || isLoading
        },
        {},
        {
          default: () => {
            return `${validate_component(Send, "Send").$$render($$result, { class: "h-4 w-4" }, {}, {})}`;
          }
        }
      )}</div> <p class="text-xs text-legal-gray-400 mt-2" data-svelte-h="svelte-e8mygg">Press Enter to send, Shift+Enter for new line</p></div>`;
    }
  })}`;
});
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  return `${$$result.head += `<!-- HEAD_svelte-14muczu_START -->${$$result.title = `<title>Legal Chatbot - Verdict360</title>`, ""}<meta name="description" content="AI-powered legal assistance for South African law"><!-- HEAD_svelte-14muczu_END -->`, ""} <div class="min-h-screen bg-legal-gray-50"> <header class="bg-white border-b border-legal-gray-200"><div class="legal-container py-4"><div class="flex items-center justify-between"><div class="flex items-center space-x-4"><a href="/" class="flex items-center text-legal-gray-600 hover:text-legal-primary">${validate_component(Arrow_left, "ArrowLeft").$$render($$result, { class: "h-5 w-5 mr-2" }, {}, {})}
            Back to Home</a></div> <div class="text-center" data-svelte-h="svelte-4lrepq"><h1 class="text-xl font-semibold text-legal-gray-900">Legal Chatbot Demo</h1> <p class="text-sm text-legal-gray-500">Professional AI legal assistance</p></div> <div class="w-24"></div> </div></div></header>  <main class="py-8"><div class="legal-container"><div class="max-w-4xl mx-auto"><div class="grid grid-cols-1 lg:grid-cols-3 gap-8"> <div class="lg:col-span-2">${validate_component(ChatWidget, "ChatWidget").$$render($$result, {}, {}, {})}</div>  <div class="space-y-6" data-svelte-h="svelte-1s3wz4j"> <div class="card-legal p-6"><h3 class="font-semibold text-legal-gray-900 mb-4">Legal AI Features</h3> <ul class="space-y-3 text-sm text-legal-gray-600"><li class="flex items-start"><span class="w-2 h-2 bg-legal-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  SA legal citation verification</li> <li class="flex items-start"><span class="w-2 h-2 bg-legal-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Constitutional Court references</li> <li class="flex items-start"><span class="w-2 h-2 bg-legal-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  POPIA compliance guidance</li> <li class="flex items-start"><span class="w-2 h-2 bg-legal-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Professional legal drafting</li></ul></div>  <div class="card-legal p-6"><h3 class="font-semibold text-legal-gray-900 mb-4">Need Help?</h3> <p class="text-sm text-legal-gray-600 mb-4">Our legal experts are available for consultations</p> <a href="/consultation" class="btn-legal-accent w-full text-center block">Book Consultation</a></div>  <div class="bg-legal-warning/10 border border-legal-warning/20 rounded-legal p-4"><p class="text-xs text-legal-gray-600"><strong>Disclaimer:</strong> This AI provides general legal information only. 
                Always consult with qualified legal professionals for specific legal advice.</p></div></div></div></div></div></main></div>`;
});
export {
  Page as default
};
