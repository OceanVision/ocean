package vision.ocean.helpers;

import android.util.Log;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.CookieStore;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

public final class MyHttpClient {

    // Set the timeout in milliseconds until a connection is established.
    // The default value is zero, that means the timeout is not used.
    private final static int TIMEOUT_CONNECTION = 3000;
    // Set the default socket timeout (SO_TIMEOUT)
    // in milliseconds which is the timeout for waiting for data.
    private final static int TIMEOUT_SOCKET = 0;

    // Based on given request, download data and cookies from web service.
    static String runRequestWithCookies(HttpUriRequest request, CookieStore cookieStore) {
        HttpParams httpParameters = new BasicHttpParams();
        HttpConnectionParams.setConnectionTimeout(httpParameters, TIMEOUT_CONNECTION);
        HttpConnectionParams.setSoTimeout(httpParameters, TIMEOUT_SOCKET);

        DefaultHttpClient httpClient = new DefaultHttpClient(httpParameters);
        httpClient.setCookieStore(cookieStore);

        ResponseHandler<String> handler = new BasicResponseHandler();
        String response = null;
        try {
            response = httpClient.execute(request, handler);
        } catch (ClientProtocolException e) {
            Log.e("ClientProtocolException", e.toString());
            e.printStackTrace();
        } catch (IOException e) {
            Log.e("IOException", e.toString());
            e.printStackTrace();
        }

        return response;
    }

    // Based on given request, download data from web service and return it as simple String.
    static public String runJsonRequest(HttpUriRequest request) {
        // Sets a request header so the service receiving the request.
        request.setHeader("Accept", "application/json");
        request.setHeader("Content-type", "application/json");

        HttpParams httpParameters = new BasicHttpParams();
        HttpConnectionParams.setConnectionTimeout(httpParameters, TIMEOUT_CONNECTION);
        HttpConnectionParams.setSoTimeout(httpParameters, TIMEOUT_SOCKET);

        DefaultHttpClient httpClient = new DefaultHttpClient(httpParameters);

        ResponseHandler<String> handler = new BasicResponseHandler();
        String response = null;
        try {
            response = httpClient.execute(request, handler);
        } catch (ClientProtocolException e) {
            Log.e("ClientProtocolException", e.toString());
            e.printStackTrace();
        } catch (IOException e) {
            Log.e("IOException", e.toString());
            e.printStackTrace();
        }

        return response;
    }

    // Parse returned String to JsonArray, if possible.
    static public JSONArray getJSONArray(HttpUriRequest request) {
        JSONArray jsonArray = null;
        try {
            jsonArray = new JSONArray(runJsonRequest(request));
        } catch (JSONException e) {
            Log.e("JSONException", e.toString());
            e.printStackTrace();
        }

        return jsonArray;
    }

    // Parse returned String to JsonObject, if possible.
    static public JSONObject getJSONObjectWithCookies(HttpUriRequest request, CookieStore cookieStore) {
        JSONObject jsonObject = null;
        try {
            jsonObject = new JSONObject(runRequestWithCookies(request, cookieStore));
        } catch (JSONException e) {
            Log.e("JSONException", e.toString());
            e.printStackTrace();
        }

        return jsonObject;
    }

    // Parse returned String to JsonObject, if possible.
    static public JSONObject getJSONObject(HttpUriRequest request) {
        JSONObject jsonObject = null;
        try {
            jsonObject = new JSONObject(runJsonRequest(request));
        } catch (JSONException e) {
            Log.e("JSONException", e.toString());
            e.printStackTrace();
        }

        return jsonObject;
    }
}
