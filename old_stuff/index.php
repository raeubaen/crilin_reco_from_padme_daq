<?php
// Original author: Rafael Teixeira De Lima <rafael.teixeira.de.lima@cern.ch>
// Editing author: Matthew Feickert <matthew.feickert@cern.ch>
// Updated for JSROOT inline display with filenames + flexbox layout by ChatGPT
?>
<html>
<head>
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"/>
<meta http-equiv="Pragma" content="no-cache"/>
<meta http-equiv="Expires" content="0"/>
<title><?php echo htmlspecialchars(getcwd()); ?></title>
<style>
  body { font-family: Arial, sans-serif; }
  /* Container for all plots - flexbox grid */
  .plots-container {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
  }
  /* Individual plot box */
  .plot-thumb {
    border: 1px solid #ddd;
    padding: 8px;
    max-width: 600px; /* same as image max width */
    flex: 1 1 600px;  /* grow/shrink with min width 350px */
    box-sizing: border-box;
  }
  .plot-thumb h3 {
    margin: 0 0 6px 0;
    font-size: 1em;
    word-break: break-all;
  }
  .plot-thumb img {
    max-width: 100%;  /* responsive inside container */
    height: auto;
    display: block;
    margin-bottom: 8px;
  }
  .file-links a {
    margin-right: 10px;
    color: blue;
    text-decoration: underline;
    cursor: pointer;
  }
  .jsroot-container {
    margin-top: 10px;
    width: 100%;    /* full width of plot box */
    height: 600px;
    border: 1px solid #ccc;
    display: none; /* hidden initially */
  }
</style>
</head>
<body>
<h1><?php echo htmlspecialchars(getcwd()); ?></h1>

<h2>Plots</h2>

<p><form>Filter: <input type="text" name="match" size="30" value="<?php if (isset($_GET['match'])) echo htmlspecialchars($_GET['match']); ?>" /><input type="submit" value="Go" /></form></p>

<div class="plots-container">
<?php
$displayed = [];
array_push($displayed, basename($_SERVER['PHP_SELF']));

$match = isset($_GET['match']) ? $_GET['match'] : '';

$files = glob("*.png");
sort($files);

foreach ($files as $pngfile) {
    if ($match && !fnmatch("*$match*", $pngfile)) continue;

    $basename = pathinfo($pngfile, PATHINFO_FILENAME);
    $pdffile = $basename . '.pdf';
    $rootfile = $basename . '.root';
    $objname = $basename . '_canvas';  // naming convention for ROOT object

    echo "<div class='plot-thumb'>\n";

    // Show filename as heading
    echo "<h3>" . htmlspecialchars($pngfile) . "</h3>\n";

    // PNG image preview
    echo "<a href=\"$pngfile\" target=\"_blank\"><img src=\"$pngfile\" alt=\"$pngfile\"></a>\n";

    // Links for PDF and JSROOT
    echo "<div class='file-links'>\n";
    if (file_exists($pdffile)) {
        echo "<a href=\"$pdffile\" target=\"_blank\">[PDF]</a>";
        $displayed[] = $pdffile;
    }
    if (file_exists($rootfile)) {
        $jsroot_url = "jsroot_viewer.php?file=" . urlencode($rootfile);
        echo "<a href=\"$jsroot_url\" target=\"_blank\">[JSROOT]</a>";
    }    echo "</div>\n";

    // Container for JSROOT interactive plot, hidden by default
    $divid = "jsroot_" . $basename;
    echo "<div id=\"$divid\" class='jsroot-container'></div>\n";

    echo "</div>\n";
}
?>
</div>

<div style="display: block; clear:both;">
<h2>Other files</h2>
<ul>
<?php
foreach (glob("*") as $filename) {
    if ((isset($_GET['noplots']) && $_GET['noplots']) || !in_array($filename, $displayed)) {
        if ($match && !fnmatch("*$match*", $filename)) continue;
        if (is_dir($filename)) {
            echo "<li>[DIR] <a href=\"$filename\">$filename</a></li>";
        } else {
            echo "<li><a href=\"$filename\">$filename</a></li>";
        }
    }
}
?>
</ul>
</div>

<script type="module">
import * as JSROOT from 'https://root.cern/js/latest/modules/main.mjs';

document.querySelectorAll('a.jsroot-link').forEach(link => {
  link.addEventListener('click', async event => {
    event.preventDefault();
    const rootfile = link.dataset.rootfile;
    const objname = link.dataset.objname;
    const divid = 'jsroot_' + objname.replace('_canvas','');

    const container = document.getElementById(divid);

    if (container.style.display === 'none' || container.style.display === '') {
      container.style.display = 'block';

      if (!container.hasChildNodes()) {
        try {
          const file = await JSROOT.openFile(rootfile);
          const obj = await file.readObject(objname);
          JSROOT.draw(divid, obj, '');
        } catch(e) {
          container.textContent = 'Failed to load ROOT object.';
          console.error(e);
        }
      }
    } else {
      container.style.display = 'none';
    }
  });
});
</script>

</body>
</html>
