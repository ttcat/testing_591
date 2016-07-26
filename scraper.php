<?php
// This is a template for a PHP scraper on morph.io (https://morph.io)
// including some code snippets below that you should find helpful

require 'vendor/autoload.php';

require 'vendor/openaustralia/scraperwiki/scraperwiki.php';
require 'vendor/openaustralia/scraperwiki/simple_html_dom.php';

//
// Read in a page
$html = scraperwiki::scrape("https://m.591.com.tw/mobile-list.html?type=rent8&version=1&o=31&regionid=3&sectionidStr=38&kind=8");

// Find something on the page using css selectors
$dom = new simple_html_dom();
$dom->load($html);

$row = (array) $dom->find(".data");

// print_r($row);
$new_row = array();

foreach ($row as $k => $v) {
	
	$new_row[$k]['data-house'] = $v->attr['data-house'];
	
	$n1 = $v->find(".n1");
	$n2 = $v->find(".n2");
	$n3 = $v->find(".n3");
	
	$new_row[$k]['url'] = "https://m.591.com.tw/mobile-detail.html?type=rent&regionid=3&sectionidStr=38&price=&room=&area=&kind=8&shape=&firstRow=0&houseId=" .$v->attr['data-house']. "&hash=16";

	$new_row[$k]['desc_1'] = $n1[0]->children[0]->nodes[0]->_[4];
	$new_row[$k]['desc_2'] = $n2[0]->children[0]->parent->nodes[1]->_[4];
	$new_row[$k]['desc_3'] = $n3[0]->nodes[0]->_[4];

}


print_r($new_row);


//
// // Write out to the sqlite database using scraperwiki library
// scraperwiki::save_sqlite(array('name'), array('name' => 'susan', 'occupation' => 'software developer'));
//
// // An arbitrary query against the database
// scraperwiki::select("* from data where 'name'='peter'")

// You don't have to do things with the ScraperWiki library.
// You can use whatever libraries you want: https://morph.io/documentation/php
// All that matters is that your final data is written to an SQLite database
// called "data.sqlite" in the current working directory which has at least a table
// called "data".
?>
