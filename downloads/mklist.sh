echo '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>'
echo '<ul>'
for f in */* *
do
	echo '<li><a href='$f'>'$f'</li>'
done

echo '</ul>'

echo '</body></html>'

