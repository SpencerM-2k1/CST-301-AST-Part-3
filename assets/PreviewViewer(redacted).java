package org.jabref.gui.preview;

import java.io.IOException;
import java.net.MalformedURLException;
import java.util.Objects;
import java.util.Optional;
import java.util.regex.Pattern;

import javafx.beans.InvalidationListener;
import javafx.beans.Observable;
import javafx.beans.value.ChangeListener;
import javafx.concurrent.Worker;
import javafx.print.PrinterJob;
import javafx.scene.control.ScrollPane;
import javafx.scene.input.ClipboardContent;
import javafx.scene.web.WebView;

import org.jabref.gui.ClipBoardManager;
import org.jabref.gui.DialogService;
import org.jabref.gui.Globals;
import org.jabref.gui.StateManager;
import org.jabref.gui.desktop.JabRefDesktop;
import org.jabref.gui.theme.ThemeManager;
import org.jabref.gui.util.BackgroundTask;
import org.jabref.gui.util.TaskExecutor;
import org.jabref.logic.exporter.ExporterFactory;
import org.jabref.logic.l10n.Localization;
import org.jabref.logic.preview.PreviewLayout;
import org.jabref.logic.search.SearchQuery;
import org.jabref.logic.util.WebViewStore;
import org.jabref.model.database.BibDatabaseContext;
import org.jabref.model.entry.BibEntry;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.events.EventTarget;
import org.w3c.dom.html.HTMLAnchorElement;

/**
 * Displays an BibEntry using the given layout format.
 */
public class PreviewViewer extends ScrollPane implements InvalidationListener {

    private static final Logger LOGGER = LoggerFactory.getLogger(PreviewViewer.class);

    // https://stackoverflow.com/questions/5669448/get-selected-texts-html-in-div/5670825#5670825
    private static final String JS_GET_SELECTION_HTML_SCRIPT = "String 1";
    private static final String JS_HIGHLIGHT_FUNCTION =
            "String 2";
    // This is a string format, and it takes a variable name as an argument to pass to the markInstance.markRegExp() Javascript method.
    private static final String JS_MARK_REG_EXP_CALLBACK =
            "String 3";

    // This is a string format, and it takes a variable name as an argument to pass to the markInstance.unmark() Javascript method.
    private static final String JS_UNMARK_WITH_CALLBACK =
            "String 4";
    private static final Pattern UNESCAPED_FORWARD_SLASH = Pattern.compile("(?<!\\\\)/");

    private final ClipBoardManager clipBoardManager;
    private final DialogService dialogService;

    private final TaskExecutor taskExecutor = Globals.TASK_EXECUTOR;
    private final WebView previewView;
    private PreviewLayout layout;

    /**
     * The entry currently shown
     */
    private Optional<BibEntry> entry = Optional.empty();
    private Optional<Pattern> searchHighlightPattern = Optional.empty();

    private final BibDatabaseContext database;
    private boolean registered;

    private final ChangeListener<Optional<SearchQuery>> listener = (queryObservable, queryOldValue, queryNewValue) -> {
        searchHighlightPattern = queryNewValue.flatMap(SearchQuery::getJavaScriptPatternForWords);
        highlightSearchPattern();
    };

    /**
     * @param database Used for resolving strings and pdf directories for links.
     */
    public PreviewViewer(BibDatabaseContext database,
                         DialogService dialogService,
                         StateManager stateManager,
                         ThemeManager themeManager) {
        this.database = Objects.requireNonNull(database);
        this.dialogService = dialogService;
        this.clipBoardManager = Globals.getClipboardManager();

        setFitToHeight(true);
        setFitToWidth(true);
        previewView = WebViewStore.get();
        setContent(previewView);
        previewView.setContextMenuEnabled(false);

        previewView.getEngine().getLoadWorker().stateProperty().addListener((observable, oldValue, newValue) -> {

            if (newValue != Worker.State.SUCCEEDED) {
                return;
            }
            if (!registered) {
                stateManager.activeSearchQueryProperty().addListener(listener);
                registered = true;
            }
            highlightSearchPattern();

            // https://stackoverflow.com/questions/15555510/javafx-stop-opening-url-in-webview-open-in-browser-instead
            NodeList anchorList = previewView.getEngine().getDocument().getElementsByTagName("a");
            for (int i = 0; i < anchorList.getLength(); i++) {
                Node node = anchorList.item(i);
                EventTarget eventTarget = (EventTarget) node;
                eventTarget.addEventListener("click", evt -> {
                    EventTarget target = evt.getCurrentTarget();
                    HTMLAnchorElement anchorElement = (HTMLAnchorElement) target;
                    String href = anchorElement.getHref();
                    if (href != null) {
                        try {
                            JabRefDesktop.openBrowser(href);
                        } catch (MalformedURLException exception) {
                            LOGGER.error("Invalid URL", exception);
                        } catch (IOException exception) {
                            LOGGER.error("Invalid URL Input", exception);
                        }
                    }
                    evt.preventDefault();
                }, false);
            }
        });

        themeManager.installCss(previewView.getEngine());
    }

    private void highlightSearchPattern() {
        String pattern = searchHighlightPattern.get().pattern().replace("\\Q", "").replace("\\E", "");
        String callbackForUnmark = "";
        if (searchHighlightPattern.isPresent()) {
            String javaScriptRegex = createJavaScriptRegex(searchHighlightPattern.get());
            callbackForUnmark = String.format(JS_MARK_REG_EXP_CALLBACK, javaScriptRegex);
            previewView.getEngine().executeScript("highlight('" + pattern + "');");
        }
    }

    /**
     * Returns the String representation of a JavaScript regex object. The method does not take into account differences between the regex implementations in Java and JavaScript.
     *
     * @param regex Java regex to print as a JavaScript regex
     * @return JavaScript regex object
     */
    private static String createJavaScriptRegex(Pattern regex) {
        String pattern = regex.pattern();
        // Create a JavaScript regular expression literal (https://ecma-international.org/ecma-262/10.0/index.html#sec-literals-regular-expression-literals)
        // Forward slashes are reserved to delimit the regular expression body. Hence, they must be escaped.
        pattern = UNESCAPED_FORWARD_SLASH.matcher(pattern).replaceAll("\\\\/");
        return "/" + pattern + "/gmi";
    }

    public void setLayout(PreviewLayout newLayout) {
        // Change listeners might set the layout to null while the update method is executing, therefore we need to prevent this here
        if (newLayout == null) {
            return;
        }
        layout = newLayout;
        update();
    }

    public void setEntry(BibEntry newEntry) {
        // Remove update listener for old entry
        entry.ifPresent(oldEntry -> {
            for (Observable observable : oldEntry.getObservables()) {
                observable.removeListener(this);
            }
        });

        entry = Optional.of(newEntry);

        // Register for changes
        for (Observable observable : newEntry.getObservables()) {
            observable.addListener(this);
        }
        update();
    }

    private void update() {
        if (entry.isEmpty() || (layout == null)) {
            // Nothing to do
            return;
        }

        ExporterFactory.entryNumber = 1; // Set entry number in case that is included in the preview layout.

        BackgroundTask
                .wrap(() -> layout.generatePreview(entry.get(), database))
                .onRunning(() -> setPreviewText("<i>" + Localization.lang("Processing %0", Localization.lang("Citation Style")) + ": " + layout.getDisplayName() + " ..." + "</i>"))
                .onSuccess(this::setPreviewText)
                .onFailure(exception -> {
                    LOGGER.error("Error while generating citation style", exception);
                    setPreviewText(Localization.lang("Error while generating citation style"));
                })
                .executeWith(taskExecutor);
    }

    private void setPreviewText(String text) {
        String myText = JS_HIGHLIGHT_FUNCTION + "<div id=\"content\"" + text + "</div>";
        previewView.getEngine().setJavaScriptEnabled(true);
        previewView.getEngine().loadContent(myText);

        this.setHvalue(0);
    }

    public void print() {
        PrinterJob job = PrinterJob.createPrinterJob();
        boolean proceed = dialogService.showPrintDialog(job);
        if (!proceed) {
            return;
        }

        BackgroundTask
                .wrap(() -> {
                    job.getJobSettings().setJobName(entry.flatMap(BibEntry::getCitationKey).orElse("NO ENTRY"));
                    previewView.getEngine().print(job);
                    job.endJob();
                })
                .onFailure(exception -> dialogService.showErrorDialogAndWait(Localization.lang("Could not print preview"), exception))
                .executeWith(taskExecutor);
    }

    public void copyPreviewToClipBoard() {
        Document document = previewView.getEngine().getDocument();

        ClipboardContent content = new ClipboardContent();
        content.putString(document.getElementById("content").getTextContent());
        content.putHtml((String) previewView.getEngine().executeScript("document.documentElement.outerHTML"));

        clipBoardManager.setContent(content);
    }

    public void copySelectionToClipBoard() {
        ClipboardContent content = new ClipboardContent();
        content.putString(getSelectionTextContent());
        content.putHtml(getSelectionHtmlContent());

        clipBoardManager.setContent(content);
    }

    @Override
    public void invalidated(Observable observable) {
        update();
    }

    public String getSelectionTextContent() {
        return (String) previewView.getEngine().executeScript("window.getSelection().toString()");
    }

    public String getSelectionHtmlContent() {
        return (String) previewView.getEngine().executeScript(JS_GET_SELECTION_HTML_SCRIPT);
    }
}
