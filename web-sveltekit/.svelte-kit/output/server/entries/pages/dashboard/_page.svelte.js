import { c as create_ssr_component, v as validate_component, e as escape } from "../../../chunks/ssr.js";
import { B as Button, P as Phone, C as Card } from "../../../chunks/Card.js";
import { I as Icon } from "../../../chunks/Icon.js";
import { M as Message_square, U as Users, C as Chart_column } from "../../../chunks/users.js";
const File_text = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  const iconNode = [
    [
      "path",
      {
        "d": "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"
      }
    ],
    ["path", { "d": "M14 2v4a2 2 0 0 0 2 2h4" }],
    ["path", { "d": "M10 9H8" }],
    ["path", { "d": "M16 13H8" }],
    ["path", { "d": "M16 17H8" }]
  ];
  return `${validate_component(Icon, "Icon").$$render($$result, Object.assign({}, { name: "file-text" }, $$props, { iconNode }), {}, {
    default: () => {
      return `${slots.default ? slots.default({}) : ``}`;
    }
  })}`;
});
const Settings = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  const iconNode = [
    [
      "path",
      {
        "d": "M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
      }
    ],
    ["circle", { "cx": "12", "cy": "12", "r": "3" }]
  ];
  return `${validate_component(Icon, "Icon").$$render($$result, Object.assign({}, { name: "settings" }, $$props, { iconNode }), {}, {
    default: () => {
      return `${slots.default ? slots.default({}) : ``}`;
    }
  })}`;
});
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let stats = {
    totalChats: 0,
    activeClients: 0,
    consultations: 0
  };
  return `${$$result.head += `<!-- HEAD_svelte-1c3imuz_START -->${$$result.title = `<title>Dashboard - Verdict360</title>`, ""}<meta name="description" content="Legal practice management dashboard"><!-- HEAD_svelte-1c3imuz_END -->`, ""} <div class="min-h-screen bg-legal-gray-50"> <header class="bg-white border-b border-legal-gray-200"><div class="legal-container py-4"><div class="flex items-center justify-between"><div data-svelte-h="svelte-b457tf"><h1 class="text-2xl font-bold text-legal-gray-900">Legal Dashboard</h1> <p class="text-legal-gray-600">Manage your legal practice with AI assistance</p></div> <div class="flex items-center space-x-4">${validate_component(Button, "Button").$$render(
    $$result,
    {
      variant: "accent",
      size: "md",
      class: "flex items-center space-x-2"
    },
    {},
    {
      default: () => {
        return `${validate_component(Phone, "Phone").$$render($$result, { class: "h-4 w-4" }, {}, {})} <span data-svelte-h="svelte-a8v3zt">Emergency Consult</span>`;
      }
    }
  )} ${validate_component(Button, "Button").$$render($$result, { variant: "outline", size: "md" }, {}, {
    default: () => {
      return `${validate_component(Settings, "Settings").$$render($$result, { class: "h-5 w-5" }, {}, {})}`;
    }
  })}</div></div></div></header>  <main class="py-8"><div class="legal-container"> <div class="legal-grid mb-8">${validate_component(Card, "Card").$$render($$result, { class: "text-center" }, {}, {
    default: () => {
      return `<div class="flex items-center justify-center mb-3">${validate_component(Message_square, "MessageSquare").$$render($$result, { class: "h-8 w-8 text-legal-primary" }, {}, {})}</div> <div class="text-2xl font-bold text-legal-gray-900">${escape(stats.totalChats)}</div> <div class="text-sm text-legal-gray-600" data-svelte-h="svelte-1mwflpn">Total Legal Chats</div>`;
    }
  })} ${validate_component(Card, "Card").$$render($$result, { class: "text-center" }, {}, {
    default: () => {
      return `<div class="flex items-center justify-center mb-3">${validate_component(Users, "Users").$$render($$result, { class: "h-8 w-8 text-legal-accent" }, {}, {})}</div> <div class="text-2xl font-bold text-legal-gray-900">${escape(stats.activeClients)}</div> <div class="text-sm text-legal-gray-600" data-svelte-h="svelte-1u7mjxn">Active Clients</div>`;
    }
  })} ${validate_component(Card, "Card").$$render($$result, { class: "text-center" }, {}, {
    default: () => {
      return `<div class="flex items-center justify-center mb-3">${validate_component(Chart_column, "BarChart3").$$render($$result, { class: "h-8 w-8 text-legal-gold" }, {}, {})}</div> <div class="text-2xl font-bold text-legal-gray-900">${escape(stats.consultations)}</div> <div class="text-sm text-legal-gray-600" data-svelte-h="svelte-48qq5v">This Month</div>`;
    }
  })}</div>  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8"> ${validate_component(Card, "Card").$$render($$result, {}, {}, {
    default: () => {
      return `<h3 class="text-lg font-semibold text-legal-gray-900 mb-4" data-svelte-h="svelte-94dqk">Legal AI Tools</h3> <div class="space-y-3"><a href="/chatbot" class="flex items-center p-3 bg-legal-gray-50 rounded-legal hover:bg-legal-gray-100 transition-colors">${validate_component(Message_square, "MessageSquare").$$render($$result, { class: "h-5 w-5 text-legal-primary mr-3" }, {}, {})} <div data-svelte-h="svelte-mgh3us"><div class="font-medium text-legal-gray-900">Legal Chat Assistant</div> <div class="text-sm text-legal-gray-600">Get AI legal guidance with SA law citations</div></div></a> <a href="/consultation" class="flex items-center p-3 bg-legal-gray-50 rounded-legal hover:bg-legal-gray-100 transition-colors">${validate_component(Users, "Users").$$render($$result, { class: "h-5 w-5 text-legal-accent mr-3" }, {}, {})} <div data-svelte-h="svelte-1disb7x"><div class="font-medium text-legal-gray-900">Client Consultations</div> <div class="text-sm text-legal-gray-600">Schedule and manage client meetings</div></div></a> <div class="flex items-center p-3 bg-legal-gray-50 rounded-legal">${validate_component(File_text, "FileText").$$render($$result, { class: "h-5 w-5 text-legal-gold mr-3" }, {}, {})} <div data-svelte-h="svelte-1s7lc7a"><div class="font-medium text-legal-gray-900">Document Analysis</div> <div class="text-sm text-legal-gray-600">AI-powered legal document review</div></div></div></div>`;
    }
  })}  ${validate_component(Card, "Card").$$render($$result, {}, {}, {
    default: () => {
      return `<h3 class="text-lg font-semibold text-legal-gray-900 mb-4" data-svelte-h="svelte-1pf3e4o">Recent Activity</h3> <div class="space-y-3" data-svelte-h="svelte-1yn5c3"><div class="flex items-center p-3 border-l-4 border-legal-primary bg-legal-primary/5"><div class="flex-1"><div class="font-medium text-legal-gray-900">Constitutional Law Query</div> <div class="text-sm text-legal-gray-600">Client asked about freedom of expression rights</div> <div class="text-xs text-legal-gray-500 mt-1">2 hours ago</div></div></div> <div class="flex items-center p-3 border-l-4 border-legal-accent bg-legal-accent/5"><div class="flex-1"><div class="font-medium text-legal-gray-900">New Client Consultation</div> <div class="text-sm text-legal-gray-600">Property law consultation scheduled</div> <div class="text-xs text-legal-gray-500 mt-1">4 hours ago</div></div></div> <div class="flex items-center p-3 border-l-4 border-legal-gold bg-legal-gold/5"><div class="flex-1"><div class="font-medium text-legal-gray-900">Document Processed</div> <div class="text-sm text-legal-gray-600">Contract analysis completed with 95% confidence</div> <div class="text-xs text-legal-gray-500 mt-1">6 hours ago</div></div></div></div>`;
    }
  })}</div></div></main></div>`;
});
export {
  Page as default
};
