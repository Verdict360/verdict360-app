# South African English Style Guide

## 🇿🇦 Overview

This style guide ensures all Verdict360 content uses consistent South African English spelling and terminology, aligning with local legal practices and client expectations.

## 💰 Currency Standards

### Primary Currency
- **Always use**: South African Rand (ZAR)
- **Symbol**: R (not $ or USD)
- **Format**: R25,000 (with commas for thousands)
- **Monthly recurring**: R5,000/month or R5,000-R10,000 monthly

### Examples
✅ **Correct**: 
- R25,000 monthly subscription
- R1,500-R3,000 pricing tier
- ZAR currency code in APIs

❌ **Incorrect**:
- $1,000-$2,000 monthly
- USD pricing
- Dollar references

## 🔤 Spelling Standards

### Core Differences (British/SA vs American)

| American | British/South African | Context |
|----------|----------------------|---------|
| color | **colour** | CSS properties, design |
| customize | **customise** | Configuration, setup |
| optimize | **optimise** | Performance, efficiency |
| analyze | **analyse** | Data processing, reports |
| license | **licence** (noun) | Legal documents |
| license | **license** (verb) | To grant permission |
| center | **centre** | Alignment, positioning |
| organize | **organise** | Structure, management |
| behavior | **behaviour** | System responses |
| favor | **favour** | Preferences |
| honor | **honour** | Legal obligations |
| neighbor | **neighbour** | Adjacent systems |

### Technical Terms

| American | British/South African |
|----------|----------------------|
| synchronize | **synchronise** |
| initialize | **initialise** |
| finalize | **finalise** |
| categorize | **categorise** |
| prioritize | **prioritise** |
| recognize | **recognise** |
| realize | **realise** |
| specialize | **specialise** |

## 🏛️ Legal Terminology

### South African Legal Context
- Use **"law firm"** not "law office"
- Use **"practitioner"** or **"advocate"** appropriately
- Reference **"POPIA"** (Protection of Personal Information Act)
- Use **"High Court"** not "Superior Court"
- Reference **"Legal Practice Council"** for regulatory matters

### Professional Titles
- **Advocate** (Senior Counsel, Junior Counsel)
- **Attorney** (Solicitor equivalent)
- **Notary Public**
- **Conveyancer**

## 🌍 Regional Considerations

### Time Formats
- Use **24-hour format**: 14:30 (not 2:30 PM)
- Business hours: **"Monday - Friday: 08:00 - 17:00"**
- Time zone: **SAST (South African Standard Time)**

### Phone Numbers
- Format: **+27 11 123 4567**
- Mobile: **+27 82 123 4567**
- Landline patterns: **+27 [area code] [number]**

### Addresses
- Use **"Cape Town"** not "Capetown"
- **"Johannesburg"** or **"Joburg"** (informal)
- **"Pretoria"** for administrative references
- **"Durban"** for KwaZulu-Natal

## 💻 Code vs Content Standards

### ⚠️ IMPORTANT DISTINCTION

**KEEP STANDARD CODING CONVENTIONS** - Do not change:
- HTML attributes (`data-color`, not `data-colour`)
- CSS properties (`color`, not `colour`) 
- JavaScript properties (`primaryColor`, not `primaryColour`)
- Framework/library terms (`customize`, `optimize`, `analyze`)
- Technical documentation about code APIs

**CHANGE USER-FACING CONTENT** - Do change:
- UI text displayed to users
- Marketing copy and descriptions
- Documentation narrative text
- Error messages shown to clients
- Help text and tooltips

### Code Examples (Keep Standard)
```css
/* ✅ Keep standard CSS properties */
.primary-color { color: #1E40AF; }
.text-center { text-align: center; }
.customize-panel { ... }
```

```javascript
// ✅ Keep standard JavaScript conventions
const config = {
  primaryColor: '#1E40AF',
  customizeWidget: true,
  optimizePerformance: true
};
```

```html
<!-- ✅ Keep standard HTML attributes -->
<script data-color="#1E40AF" data-customize="true"></script>
```

### User-Facing Content (Change to British English)
```html
<!-- ✅ Change UI text content -->
<p>Customise your legal consultation experience</p>
<button>Optimise Settings</button>
<span>Analyse your legal documents</span>
```

```javascript
// ✅ Change user messages, keep code properties
const messages = {
  welcome: "Customise your legal experience", // British spelling
  error: "Please optimise your settings"      // British spelling
};

const config = {
  primaryColor: '#1E40AF',  // Keep standard property name
  customizeWidget: true     // Keep standard property name  
};
```

## 📝 Documentation Standards

### File Names and Headers
- Use British spelling in all documentation
- **LICENCE** not LICENSE for licence files
- **COLOUR_SCHEME.md** not COLOR_SCHEME.md

### Comments and Documentation
```javascript
/**
 * Optimises the legal widget for South African law firms
 * @param {Object} config - Customisation options
 * @param {string} config.colour - Primary brand colour
 * @returns {Object} Optimised widget configuration
 */
function optimiseWidget(config) {
  // Analyse current configuration
  const analysedConfig = analyseConfig(config);
  
  // Customise based on South African legal standards
  return customiseForSALegal(analysedConfig);
}
```

## 🤖 AI Response Guidelines

### System Prompts and Responses
All AI responses must:
- Use British/South African spelling exclusively
- Reference South African legal framework
- Use Rand (R) for all pricing
- Include appropriate South African legal context

### Example AI Responses
✅ **Correct**:
> "I can help you customise your legal consultation booking system. Our services start at R2,500 monthly, and we specialise in South African legal compliance including POPIA requirements."

❌ **Incorrect**:
> "I can help you customize your legal consultation booking system. Our services start at $150 monthly, and we specialize in legal compliance."

## 🔍 Quality Assurance

### Pre-commit Checks
1. **Spell check** against British English dictionary
2. **Currency validation** - all amounts in ZAR
3. **Legal terminology** review for SA context
4. **API response** format compliance

### Automated Tools
- Use `aspell` with British English dictionary
- Configure linters for British spelling
- Set up git hooks for currency format validation

### Manual Review Checklist
- [ ] All monetary amounts in South African Rand (R)
- [ ] British/South African spelling throughout
- [ ] South African legal terminology used correctly
- [ ] Phone numbers in +27 format
- [ ] Time references in SAST
- [ ] No American English spellings present

## 📋 Implementation Priority

### High Priority (Complete Immediately)
1. **Documentation files** (README.md, CLAUDE.md, etc.)
2. **Widget configuration** (data-colour attributes)
3. **API responses** with currency and spelling
4. **User-facing content** and error messages

### Medium Priority (Next Sprint)
1. **Code comments** and documentation
2. **Configuration files** and schemas
3. **Test files** and scenarios
4. **Development tools** and scripts

### Low Priority (Ongoing)
1. **Internal logs** and debug messages
2. **Development documentation**
3. **Third-party integration configs**

## 🚨 Common Mistakes to Avoid

### Currency Errors
- Never use $ symbol for pricing
- Avoid USD or dollar references
- Don't forget thousands separators (R25,000 not R25000)

### Spelling Traps
- "License" vs "Licence" - context matters
- "Practice" (noun) vs "Practise" (verb)
- "Advice" (noun) vs "Advise" (verb)

### Legal Context Errors
- Don't use American legal terms
- Always reference appropriate South African legislation
- Use correct professional titles (Advocate vs Attorney)

## 📞 Escalation and Questions

For questions about South African English standards:
1. **Check this guide first**
2. **Consult SA legal style guides**
3. **Reference Legal Practice Council guidelines**
4. **When in doubt, use British English spelling**

---

**Last Updated**: 2025-01-23  
**Applies to**: All Verdict360 platform content  
**Mandatory for**: Client-facing features, documentation, AI responses  
**Review frequency**: Quarterly or when major features added