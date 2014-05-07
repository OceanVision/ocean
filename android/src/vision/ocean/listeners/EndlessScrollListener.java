package vision.ocean.listeners;

import android.os.AsyncTask;
import android.support.v4.app.Fragment;
import android.widget.AbsListView;
import android.widget.AbsListView.OnScrollListener;
import org.json.JSONObject;

public class EndlessScrollListener implements OnScrollListener {

    // Number of maximum not showed records on list when next page is loaded.
    private static final int VISIBLE_TRESHOLD = 10;
    // Total number of elements is list.
    private int previousTotal = 0;
    // Is list loading new records.
    private boolean loading = true;
    // Instance of callback.
    private Callbacks mCallbacks;

    public interface Callbacks {
        /**
         * Callback when load data task is needed.
         */
        public AsyncTask<Void, Void, JSONObject> getLoadTask();
    }

    public EndlessScrollListener(Fragment fragment) {
        // Fragments using this listener must implement its callbacks.
        if (!(fragment instanceof Callbacks)) {
            throw new IllegalStateException(
                    "Fragment must implement scrolllistener's callbacks.");
        }
        this.mCallbacks = (Callbacks) fragment;
    }

    public void reset() {
        previousTotal = 0;
        loading = true;
    }

    @Override
    public void onScroll(AbsListView view, int firstVisibleItem, int visibleItemCount, int totalItemCount) {
        // If list was loading, check if loading is done.
        if (loading) {
            if (totalItemCount > previousTotal) {
                loading = false;
                previousTotal = totalItemCount;
            }
        }
        // If not loading and close enough to end (depends on threshold) load
        // new data.
        if (!loading
                && (firstVisibleItem + visibleItemCount + VISIBLE_TRESHOLD) >= totalItemCount) {
            mCallbacks.getLoadTask().execute();
            loading = true;
        }
    }

    @Override
    public void onScrollStateChanged(AbsListView view, int scrollState) {
        // Auto-generated method stub
    }
}
