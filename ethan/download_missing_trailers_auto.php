<?php
require_once("includes/config.php");

// Check if yt-dlp is installed
exec('which yt-dlp', $output, $returnCode);
if ($returnCode !== 0) {
    die("Error: yt-dlp is not installed. Please install it first with: brew install yt-dlp\n");
}

// Function to sanitize filenames
function sanitizeFilename($string) {
    // Replace spaces with underscores
    $string = str_replace(' ', '_', $string);
    // Remove any character that is not alphanumeric, underscore, or hyphen
    $string = preg_replace('/[^a-zA-Z0-9_-]/', '', $string);
    // Convert to lowercase
    return strtolower($string);
}

// Function to get entity details
function getEntityDetails($con, $entityId) {
    $query = $con->prepare("SELECT * FROM entities WHERE id = :id");
    $query->bindValue(":id", $entityId);
    $query->execute();
    
    if ($query->rowCount() == 0) {
        return null;
    }
    
    return $query->fetch(PDO::FETCH_ASSOC);
}

// Function to update entity with preview path
function updateEntityPreview($con, $entityId, $previewPath) {
    $query = $con->prepare("UPDATE entities SET preview = :preview WHERE id = :id");
    $query->bindValue(":preview", $previewPath);
    $query->bindValue(":id", $entityId);
    return $query->execute();
}

// Function to search YouTube for a trailer
function searchYouTubeTrailer($query) {
    // Sanitize the search query
    $searchQuery = urlencode($query . " trailer official");
    
    // Use yt-dlp to search for the video
    $command = "yt-dlp --get-id --max-downloads 1 ytsearch:\"$searchQuery\"";
    exec($command, $output, $returnCode);
    
    if ($returnCode !== 0 || empty($output)) {
        echo "Error searching YouTube. Output:\n";
        echo implode("\n", $output);
        return null;
    }
    
    // Get the first video ID
    $videoId = trim($output[0]);
    return "https://www.youtube.com/watch?v=$videoId";
}

// Check if the previews directory exists, create it if not
$previewsDir = __DIR__ . '/entities/previews';
if (!file_exists($previewsDir)) {
    mkdir($previewsDir, 0755, true);
    echo "Created previews directory: $previewsDir\n";
}

// Get all entities with preview paths that don't exist as files
$query = $con->query("SELECT id, name, preview FROM entities WHERE preview IS NOT NULL AND preview != '' ORDER BY name");
$entities = [];

while ($row = $query->fetch(PDO::FETCH_ASSOC)) {
    $previewPath = $row['preview'];
    $fullPath = __DIR__ . '/' . $previewPath;
    
    // Check if the file exists
    if (!file_exists($fullPath)) {
        $entities[] = $row;
    }
}

if (count($entities) == 0) {
    echo "All preview files exist. Nothing to download.\n";
    exit;
}

echo "Found " . count($entities) . " entities with missing preview files.\n";
echo "This script will automatically search YouTube for trailers and download them.\n";
echo "Note: This is for demonstration purposes only. For a production environment, you should use proper licensed content.\n\n";

// Auto-confirm (no prompt)
echo "Automatically proceeding with downloads...\n";

// Process each entity
foreach ($entities as $index => $entity) {
    $entityId = $entity['id'];
    $entityName = $entity['name'];
    $previewPath = $entity['preview'];
    
    echo "\n[$index] Processing: $entityName (ID: $entityId)\n";
    echo "Missing preview file: $previewPath\n";
    
    // Extract the filename from the preview path
    $pathInfo = pathinfo($previewPath);
    $filename = $pathInfo['basename'];
    $outputPath = "$previewsDir/$filename";
    
    // Search YouTube for a trailer
    echo "Searching YouTube for '$entityName trailer'...\n";
    $youtubeUrl = searchYouTubeTrailer($entityName);
    
    if (!$youtubeUrl) {
        echo "Could not find a trailer for '$entityName' on YouTube. Skipping.\n";
        continue;
    }
    
    echo "Found trailer: $youtubeUrl\n";
    
    // Download the video using yt-dlp
    $command = "yt-dlp -f 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/mp4' --merge-output-format mp4 -o '$outputPath' '$youtubeUrl'";
    echo "Executing: $command\n";
    exec($command, $output, $returnCode);
    
    if ($returnCode !== 0) {
        echo "Error downloading video. Output:\n";
        echo implode("\n", $output);
        continue;
    }
    
    echo "Success! Trailer downloaded for $entityName.\n";
    
    // Add a small delay to avoid overwhelming YouTube
    sleep(2);
}

echo "\nAll done! Refresh the homepage to see the trailers in action.\n";
echo "Remember to modify index.php to echo the preview if it's not showing:\n";
echo "Change: \$preview->createPreviewVideo(null);\n";
echo "To: echo \$preview->createPreviewVideo(null);\n";
?>
