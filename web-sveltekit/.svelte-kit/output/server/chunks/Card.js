import { c as create_ssr_component, v as validate_component, d as add_attribute } from "./ssr.js";
import { I as Icon } from "./Icon.js";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
const Phone = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  const iconNode = [
    [
      "path",
      {
        "d": "M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
      }
    ]
  ];
  return `${validate_component(Icon, "Icon").$$render($$result, Object.assign({}, { name: "phone" }, $$props, { iconNode }), {}, {
    default: () => {
      return `${slots.default ? slots.default({}) : ``}`;
    }
  })}`;
});
function cn(...inputs) {
  return twMerge(clsx(inputs));
}
const Button = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { variant = "primary" } = $$props;
  let { size = "md" } = $$props;
  let { disabled = false } = $$props;
  let { type = "button" } = $$props;
  const variants = {
    primary: "btn-legal-primary",
    secondary: "btn-legal-secondary",
    accent: "btn-legal-accent",
    outline: "border border-legal-primary text-legal-primary hover:bg-legal-primary hover:text-white"
  };
  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg"
  };
  if ($$props.variant === void 0 && $$bindings.variant && variant !== void 0) $$bindings.variant(variant);
  if ($$props.size === void 0 && $$bindings.size && size !== void 0) $$bindings.size(size);
  if ($$props.disabled === void 0 && $$bindings.disabled && disabled !== void 0) $$bindings.disabled(disabled);
  if ($$props.type === void 0 && $$bindings.type && type !== void 0) $$bindings.type(type);
  return `<button${add_attribute("type", type, 0)} ${disabled ? "disabled" : ""}${add_attribute("class", cn("font-medium rounded-legal transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-legal-primary focus:ring-offset-2", variants[variant], sizes[size], disabled && "opacity-50 cursor-not-allowed", $$props.class), 0)}>${slots.default ? slots.default({}) : ``}</button>`;
});
const Card = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { padding = true } = $$props;
  let { hover = false } = $$props;
  if ($$props.padding === void 0 && $$bindings.padding && padding !== void 0) $$bindings.padding(padding);
  if ($$props.hover === void 0 && $$bindings.hover && hover !== void 0) $$bindings.hover(hover);
  return `<div${add_attribute("class", cn("card-legal", padding && "p-6", hover && "hover:shadow-legal-lg transition-shadow duration-200", $$props.class), 0)}>${slots.default ? slots.default({}) : ``}</div>`;
});
export {
  Button as B,
  Card as C,
  Phone as P
};
