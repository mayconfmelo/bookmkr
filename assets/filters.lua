-- TODO: implement min-book options in epub template

function BlockQuote(el)
  -- GitHub-like [!CALLOUT] in blockquotes
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


function Div(el)
  -- Typst
  if FORMAT == "typst" then
    -- Parse Div content as Typst code
    local content = pandoc.write(pandoc.Pandoc(el.content), "typst")
      :gsub("^%s*", ""):gsub("%s*$", "")
    
    -- ::: {.dropcap}
    if el.classes:includes("dropcap") then
      content = [[
        #import "@preview/droplet:0.3.1": dropcap
        #dropcap(height: 3)[
      ]] .. content .. "\n]\n"
    
    -- ::: {.no-dropcap}
    elseif el.classes:includes("no-dropcap") then
      content = "#block[\n#let dropcap(c) = {c}\n" .. content .. "]"
    end
      
    -- ::: {.indent}
    if el.classes:includes("indent") then
      content = "#context block[\n#set par(first-line-indent: (..par.first-line-indent, all: true))\n" .. content .. "\n]\n"
  
    -- ::: {.no-indent}
    elseif el.classes:includes("no-indent") then
      content = "#context block[\n#set par(first-line-indent: (amount: 0em, all: true))\n" .. content .. "\n]\n"
    end
    
    -- ::: {.center}
    if el.classes:includes("center") then
      content = "#align(center)[\n" .. content .. "\n]\n"
  
    -- ::: {.left}
    elseif el.classes:includes("left") then
      content = "#align(left)[\n" .. content .. "\n]\n"
    
    -- ::: {.right}
    elseif el.classes:includes("right") then
      content = "#align(right)[\n" .. content .. "\n]\n"
    end
    
    return pandoc.RawBlock("typst", content)
  
  -- Other formats
  else
    return nil
  end
end


function RawInline(el)
  -- Get \n in Typst
  if el.format == "tex" and FORMAT == "typst" then
    return pandoc.RawInline("typst", el.text)
  end
end



function Meta(meta)
  -- Include CSS inside HTML files
  local include_css = {
    html = true,
    html4 = true,
    html5 = true
  }
  if include_css[FORMAT] and meta.css then
    local path = pandoc.utils.stringify(meta.css)
    local infile = io.open(path, "rb")
    if not infile then
      io.stderr:write("Error reading file: " .. source .. "\n")
      return
    end
  
    local content = infile:read("*all")
    meta.css = pandoc.MetaString(content)
    
    infile:close()
  end

  return meta
end