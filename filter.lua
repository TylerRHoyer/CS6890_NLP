local lfs = require 'lfs'
local json = require 'dkjson'
local out_root = 'processed'
local in_root = '/media/standard/DATA/twitter/keywords_3'

-- I recommend using LuaJIT, not Lua on this file. No, I mean it.
-- You will regret it if you don't.

local function union(a, b)
	for key, value in next, b do
		a[key] = value + (a[key] or 0)
	end
end

local function get(f)
	f = io.open(f, 'r')
	s = json.decode(f:read())
	f:close()
	return s
end

local lineD = '%s"%s":%d,\n'
local lineT = '%s"%s": {\n'
local function _set(f, a, l)
	for key, value in next, a do
		if type(value) == 'table' then
			f:write(lineT:format(l, key))
			_set(f, value, l .. '\t')
			f:write(l .. '},\n')
		else
			f:write(lineD:format(l, key, value))
		end
	end
end

local function set(f, a)
	f = io.open(f, 'w')
	f:write('{\n')
	_set(f, a, '')
	f:write('}\n')
	f:close()
end

local function count(t)
	local c = 0
	for key, value in next, t do
		c = c + 1
	end
	return c
end

local function merge(f, a)
	local b = get(f)
	a.count = a.count + b.count
	union(a.cnt, b.cnt)
	union(a.occ, b.occ)
end

local function inc(t, k, a)
	a = a or 1
	local c = t[k]
	if c then
		t[k] = c + a
	else
		t[k] = a
	end
end

local function merge_cor(f, a)
	for word, words in next, get(f).cor do
		for other, cnt in next, words do
			if a.cnt[word] or a.cnt[other] then
				if a.cor[word] then
					inc(a.cor[word], other, cnt)
				else
					a.cor[word] = {[other] = cnt}
				end
			end
		end
	end
end

local function process(path)
	local name = path:sub(#in_root+1):match '^(.+)%.%a+$'
	local out_path = out_root .. name .. '.json'

	if lfs.attributes(out_path, 'mode') == 'file' then
		return print('CACHED ' .. path)
	else
		print('PROCESSING ' .. path)
	end

	local count = 0
	local word_cnt = {}
	local word_occ = {}
	local word_cor = {}
	for line in io.lines(path) do
		count = count + 1

		local prv_words = {}
		local new_words = line:gmatch '[^ ]*[^ %.!%?]'
		local t = new_words()
		for word in new_words do
			inc(prv_words, word)
		end
		for word, cnt in next, prv_words do
			inc(word_cnt, word, cnt)
			inc(word_occ, word, 1)
			for other, cnt in next, prv_words do
				if word < other then
					if not word_cor[word] then
						word_cor[word] = {[other] = 1}
					else
						inc(word_cor[word], other, 1)
					end
				end
			end
		end
	end
	set(out_path, {
		count = count;
		cnt = word_cnt;
		occ = word_occ;
		cor = word_cor;
	})
end

local function traverse(path)
	for filename in lfs.dir(path) do
		local filepath = path .. '/' .. filename
		local mode = lfs.attributes(filepath, 'mode')
		if mode == 'file' then
			coroutine.yield(filepath)
		elseif mode == 'directory' then
			if not (filename == '.' or filename == '..') then
				traverse(filepath)
			end
		end
	end
end

local function _files(co, last_path)
	local status, result = coroutine.resume(co, last_path)
	if status then
		return result
	end
end

local function files(path)
	local co = coroutine.create(traverse)
	return _files, co, path
end

local function stats(results)
	print('Documents: ', result.count)
	local num_words = 0
	local num_occurances = 0
	local num_distinct_words = 0
	local i = 0
	local c = {}
	for i = 1, 19 do
		c[i] = 0
	end
	local half = result.count * 0.5
	for word, cnt in next, result.cnt do
		local occ = result.occ[word]
		if occ < 20 then
			c[occ] = c[occ] + 1
		elseif occ < half then
			i = i + 1
		end
		num_words = num_words + cnt
		num_occurances = num_occurances + occ
		num_distinct_words = num_distinct_words + 1
	end
	print('Num words:', num_words)
	print('Occ words:', num_occurances)
	print('Unq words:', num_distinct_words)
	print('Matching words:', i)
	for i, occ in ipairs(c) do
		print(i, occ)
	end
end

-- -- Process text files into statistics
-- for file_path in files(in_root) do
-- 	process(file_path)
-- end
-- local f = io.open('words.txt', 'w')
-- local cur = {}
-- for file_path in files(in_root) do
-- 	for line in io.lines(file_path) do
-- 		if line:match('^%d%d%d%d%d%d%d%d%d%d%d%d%d ') and #cur > 0 then
-- 			f:write(table.concat(cur, '\t') .. '\n')
-- 			cur = {}
-- 		end
-- 		cur[#cur + 1] = line
-- 	end
-- end
-- if #cur > 0 then
-- 	f:write(table.concat(cur, '\t') .. '\n')
-- end
-- f:close()

--[[ Collect words_3.txt ]]
-- local s = {
-- 	{name = 'seen', value = 0};
-- 	{name = 'not_loadable', value = 0};
-- 	{name = 'not_english', value = 0};
-- 	{name = 'deleted', value = 0};
-- 	{name = 'bad_form', value = 0};
-- 	{name = 'duplicates', value = 0};
-- 	{name = 'non_ce', value = 0};
-- 	{name = 'processed', value = 0};
-- }
-- local f = io.open('words_3.txt', 'w')
-- local cur = {}
-- for file_path in files(in_root) do
-- 	local get = io.lines(file_path)
-- 	local line
-- 	while true do
-- 		line = get(line)
-- 		if line and #line > 0 then
-- 			f:write(line .. '\n')
-- 		else
-- 			break
-- 		end
-- 	end
-- 	if line then
-- 		line = get(line)
-- 		local i = 1
-- 		for num in line:gmatch '%d+' do
-- 			s[i].value = s[i].value + tonumber(num)
-- 			i = i + 1
-- 		end
-- 	end
-- end
-- f:close()
-- for i, t in ipairs(s) do
-- 	print(i, t.name, t.value)
-- end

--[[ Convert words_3.txt into words_3_filtered.txt ]]
-- local keywords = {
	-- 'clean energy',
	-- 'energy generation',
	-- 'renewable energy',
	-- 'carbon-free',
	-- 'zero emission',
	-- 'solar power',
	-- 'nuclear power',
	-- 'wind power',
	-- 'geothermal',
	-- 'hydropower',
	-- 'pollution',
	-- 'coal power',
	-- 'coal plant',
	-- 'coal generation',
	-- 'electric vehicle',
	-- ' ev ',
	-- 'biofuel',
	-- 'co2',
	-- 'co 2',
	-- 'carbon dioxide',
	-- 'greenhouse',
	-- 'carbon neutral',
	-- 'carbon free',
	-- 'carbon-free',
	-- 'carbon-neutral',
-- }
-- local f = io.open('word_3_filtered.txt', 'w')
-- for line in io.lines 'words_3.txt' do
-- 	for i, phrase in ipairs(keywords) do
-- 		if line:match(phrase) then
-- 			f:write(line .. '\n')
-- 		end
-- 	end
-- end
-- f:close()

--[[ Subsample word_3_filtered.txt into final.txt ]]
local times = {}
local posts = {}
print('Creating')
local m = 0
local p = 0
local w = 0
for line in io.lines 'word_3_filtered.txt' do
	m = m + 1
	local t = tonumber(line:sub(1, 13))
	if t then
		p = p + 1
		if posts[t] then
			posts[t][line] = true
		else
			posts[t] = {[line] = true}
			times[#times + 1] = t
		end
	end
end
print(m)
print('Sorting')
table.sort(times)
print('Sampling')
local result = {}
local factor = 1
for i = 1, math.floor(#times / factor) do
	result[i] = next(posts[times[factor*i]])
end
print(#result)
print('Writing')
local f = io.open('final.txt', 'w')
f:write(table.concat(result, '\n'))
f:close()


--Merge statics (besides correlation matrix)
-- print 'Loading'
-- local result = get('totals_2019.json')
-- print 'Loaded'

-- print('Documents: ', result.count)
-- local half = result.count * 0.5
-- for word, occ in next, result.occ do
-- 	if occ < 20 or occ > half then
-- 		result.occ[word] = nil
-- 		result.cnt[word] = nil
-- 	end
-- end
-- set('words_2019_2.json', result)

-- print 'Loading'
-- local result = get('totals_2019.json')
-- result.cor = {}
-- print 'Loaded'

-- local i = 0
-- local j = 0
-- for line in io.open('cor_2019_2.ncol'):lines() do
-- 	i = i + 1
-- 	for a, b, c in line:gmatch '([^ ]) ([^ ]) (%d+)' do
-- 		j = j + 1
-- 		c = tonumber(c)

-- 		local t = result.cor

-- 		if not t[a] then
-- 			t[a] = {}
-- 		end
-- 		t = t[a]

-- 		if t[b] then
-- 			t[b] = t[b] + c
-- 		else
-- 			t[b] = c
-- 		end
-- 	end
-- end
-- print(i, j)

-- local keywords = {
-- 	'energy',
-- 	'renewable',
-- 	'coal',
-- 	'solar',
-- 	'power',
-- 	'electric'
-- }

-- result.cor = {}
-- for file_path in files(out_root .. '/2019') do
-- 	print('MERGE CORRELLATION', file_path)
-- 	merge_cor(file_path, result)
-- end
-- print 'writing'

-- local lines = {}
-- f = io.open('cor_2019_2.ncol', 'w')
-- for w1, row in next, result.cor do
-- 	for w2, weight in next, row do
-- 		lines[#lines + 1] = w1 .. ' ' .. w2 .. ' ' .. tostring(weight)
-- 	end
-- 	if #lines >= 10000 then
-- 		f:write(table.concat(lines, '\n') .. '\n')
-- 		lines = {}
-- 	end
-- end
-- f:write(table.concat(lines, '\n'))
-- f:close()

-- for file_path in files('processed/2019') do
-- 	print('MERGING ' .. file_path)
-- 	merge(file_path, result)
-- end
-- set('totals_2019.json', result)
