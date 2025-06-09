-- TODO: implement min-book options in epub template

-- GitHub-like [!CALLOUT] in blockquotes
function BlockQuote(el)
  print(el)
  
  local content = el.content
  for i, blk in ipairs(content) do
    if blk.t == "Para" and #blk.c > 0 then
      local first = blk.c[1]
      if first.t == "Str" and first.text:match("^%[%!.*%]") then
        local label = first.text:match("^%[%!(.-)%]")
        blk.c[1] = pandoc.Strong{pandoc.Str(label .. ":")}
        table.insert(blk.c, 2, pandoc.LineBreak())
      
        el = pandoc.Div(el, {class = 'box'})
      end
    end
  end
  return el
end