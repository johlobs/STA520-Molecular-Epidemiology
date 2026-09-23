-- _quiz-filter.lua
-- Transforms .quiz divs into sta520-quiz HTML at build time.
--
-- Authoring format:
--
--   :::: {.quiz}
--   Question text here?
--
--   ::: {.ctx}
--   ```
--   R output / table goes here (preformatted)
--   ```
--   :::
--
--   - Wrong option
--   - **Correct option**   ← bold = correct answer
--   - Another wrong option
--
--   ::: {.exp}
--   Explanation shown after answering.
--   :::
--   ::::
--
-- The .ctx and .exp divs are optional.
-- Multiple options can be marked correct (bold).

local function has_class(el, cls)
  if not el.classes then return false end
  for _, c in ipairs(el.classes) do
    if c == cls then return true end
  end
  return false
end

local function esc_attr(s)
  s = s:gsub('&', '&amp;')
  s = s:gsub('"', '&quot;')
  s = s:gsub('\n', ' ')
  return s
end

local function esc_html(s)
  s = s:gsub('&', '&amp;')
  s = s:gsub('<', '&lt;')
  s = s:gsub('>', '&gt;')
  return s
end

-- An item is correct if its first inline is Strong (bold)
local function is_correct(item)
  if #item == 0 then return false end
  local b = item[1]
  if (b.t == "Plain" or b.t == "Para") and #b.content > 0 then
    return b.content[1].t == "Strong"
  end
  return false
end

-- Extract text from a .ctx div: prefer CodeBlock content (preserves whitespace)
local function get_ctx_text(div)
  for _, b in ipairs(div.content) do
    if b.t == "CodeBlock" then return b.text end
  end
  return pandoc.utils.stringify(div)
end

function Div(el)
  if not has_class(el, "quiz") then return nil end

  local question_parts = {}
  local ctx_text       = nil
  local options        = {}
  local exp_text       = nil
  local past_question  = false

  for _, block in ipairs(el.content) do
    if block.t == "Div" and has_class(block, "ctx") then
      ctx_text    = get_ctx_text(block)
      past_question = true
    elseif block.t == "Div" and has_class(block, "exp") then
      exp_text = pandoc.utils.stringify(block)
    elseif block.t == "BulletList" then
      past_question = true
      for _, item in ipairs(block.content) do
        table.insert(options, {
          text    = pandoc.utils.stringify(item),
          correct = is_correct(item)
        })
      end
    elseif (block.t == "Para" or block.t == "Plain") and not past_question then
      table.insert(question_parts, pandoc.utils.stringify(block))
    end
  end

  local question = table.concat(question_parts, " ")

  local html = {}
  html[#html+1] = '<div class="sta520-quiz" data-question="' .. esc_attr(question) .. '">'

  if ctx_text then
    html[#html+1] = '  <div class="q-ctx">' ..
                    '<pre style="margin:0;font-size:0.82rem;">' ..
                    esc_html(ctx_text) .. '</pre></div>'
  end

  for _, opt in ipairs(options) do
    html[#html+1] = '  <div class="q-opt" data-correct="' ..
                    (opt.correct and "true" or "false") .. '">' ..
                    opt.text .. '</div>'
  end

  if exp_text then
    html[#html+1] = '  <div class="q-exp">' .. exp_text .. '</div>'
  end

  html[#html+1] = '</div>'
  return pandoc.RawBlock('html', table.concat(html, '\n'))
end
